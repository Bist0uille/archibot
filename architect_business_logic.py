"""
Logique métier spécialisée pour les architectes
Conforme aux pratiques professionnelles et à la réglementation française
"""
from typing import Dict, List, Any

# Base de données des CERFA et de leurs propriétés
CERFA_DATABASE = {
    "13406-15": {"nom": "Permis de construire pour une maison individuelle (PCMI)", "delai": 60},
    "13409-15": {"nom": "Permis de construire (autre)", "delai": 90},
    "13703-12": {"nom": "Déclaration préalable (maison individuelle)", "delai": 30},
    "13404-12": {"nom": "Déclaration préalable (générale)", "delai": 30},
    "16297-03": {"nom": "Permis d'aménager", "delai": 90},
    "16700-01": {"nom": "Modification d'un permis de construire", "delai": 60},
    "13405-13": {"nom": "Permis de démolir", "delai": 60},
    "13824-04": {"nom": "Autorisation de travaux pour un ERP", "delai": 120},
    "13407-10": {"nom": "Déclaration d'ouverture de chantier (DOC)", "delai": 0},
    "13408-12": {"nom": "Déclaration attestant l'achèvement des travaux (DAACT)", "delai": 0},
    "13410-12": {"nom": "Certificat d'urbanisme", "delai": 0},
    "DC1": {"nom": "Lettre de candidature (Marché public)", "delai": 0},
    "DC2": {"nom": "Déclaration du candidat (Marché public)", "delai": 0},
    "DC4": {"nom": "Déclaration de sous-traitance (Marché public)", "delai": 0},
}

class ArchitectBusinessLogic:
    """Logique métier pour déterminer les documents et alertes nécessaires."""

    def analyser_projet(self, donnees_projet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les données d'un projet pour déterminer les CERFA requis,
        les alertes et les délais d'instruction.
        """
        projet = donnees_projet.get('projet', {})
        client = donnees_projet.get('client', {})
        technique = donnees_projet.get('technique', {})

        type_projet = projet.get('typeProjet', '')
        surface = float(projet.get('surfacePlancher', 0.0))
        surface_terrain = float(projet.get('surfaceTerrain', 0.0))
        is_entreprise = bool(client.get('numeroSiret'))
        zone_protegee = technique.get('zoneProtegee', False)
        demolition = technique.get('demolition', False)
        is_erp = projet.get('destination') == 'erp'

        autorisations = []
        alertes = []
        delai_total = 0

        # --- Logique de sélection des CERFA ---

        if type_projet == 'construction_neuve':
            if is_entreprise:
                autorisations.append({"type": "13409-15", "obligatoire": True})
            else:
                if surface <= 150:
                    autorisations.append({"type": "13406-15", "obligatoire": True})
                else:
                    autorisations.append({"type": "13409-15", "obligatoire": True})
        
        elif type_projet == 'extension':
            if 0 <= surface <= 20:
                if zone_protegee:
                    autorisations.append({"type": "13703-12", "obligatoire": True})
            elif 21 <= surface <= 40:
                autorisations.append({"type": "13703-12", "obligatoire": True})
            elif surface > 40:
                if is_entreprise:
                    autorisations.append({"type": "13409-15", "obligatoire": True})
                else:
                    autorisations.append({"type": "13406-15", "obligatoire": True})

        elif type_projet == 'renovation':
            if is_entreprise:
                 autorisations.append({"type": "13404-12", "obligatoire": True})
            else:
                 autorisations.append({"type": "13703-12", "obligatoire": True})
            if surface > 40:
                autorisations.append({"type": "13409-15", "obligatoire": True})

        elif type_projet == 'amenagement':
            if surface_terrain <= 2500:
                autorisations.append({"type": "13404-12", "obligatoire": True})
            else:
                autorisations.append({"type": "16297-03", "obligatoire": True})

        elif type_projet == 'modification':
            autorisations.append({"type": "16700-01", "obligatoire": True})

        elif type_projet == 'appel_offres_public':
            autorisations.append({"type": "DC1", "obligatoire": True})
            autorisations.append({"type": "DC2", "obligatoire": True})
            if technique.get('sousTraitance'):
                autorisations.append({"type": "DC4", "obligatoire": True})

        # --- Situations spéciales ---
        if demolition:
            autorisations.append({"type": "13405-13", "obligatoire": True})
        if is_erp:
            autorisations.append({"type": "13824-04", "obligatoire": True})

        # --- Documents toujours générés (sauf cas spécifiques) ---
        if type_projet not in ['modification', 'appel_offres_public']:
            autorisations.append({"type": "13407-10", "obligatoire": True})
            autorisations.append({"type": "13408-12", "obligatoire": True})
            autorisations.append({"type": "13410-12", "obligatoire": False}) # Optionnel

        # --- Alertes automatiques ---
        if not is_entreprise and surface > 150:
            alertes.append({"message": "Architecte obligatoire (surface > 150m² pour un particulier)."})
        if is_entreprise and type_projet in ['construction_neuve', 'extension']:
             alertes.append({"message": "Architecte obligatoire pour une personne morale."})

        if surface > 50: # RT2012/RE2020 s'applique aux extensions > 50m2
            alertes.append({"message": "Étude thermique (RT2012/RE2020) probablement requise."})
        if surface_terrain > 1000:
            alertes.append({"message": "Étude de sol recommandée."})
        if zone_protegee:
            alertes.append({"message": "Avis de l'Architecte des Bâtiments de France (ABF) requis."})

        # --- Calcul du délai d'instruction ---
        delais = [CERFA_DATABASE[doc["type"]]["delai"] for doc in autorisations if doc["obligatoire"]]
        if delais:
            delai_total = max(delais)
            if zone_protegee:
                delai_total += 15
                alertes.append({"message": f"Délais d'instruction rallongés de 15 jours (total: {delai_total} jours)."})

        # --- Formatage final ---
        autorisations_formatees = []
        for doc in autorisations:
            cerfa_info = CERFA_DATABASE.get(doc["type"], {})
            autorisations_formatees.append({
                "type": f"CERFA {doc['type']}",
                "nom": cerfa_info.get("nom", "Document inconnu"),
                "delai_instruction": cerfa_info.get("delai", 0),
                "obligatoire": doc["obligatoire"]
            })

        return {
            "analyse_reglementaire": {
                "autorisations_requises": autorisations_formatees,
                "alertes_conformite": alertes,
                "delai_instruction_estime_jours": delai_total
            }
        }
