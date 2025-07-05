"""
Système de formulaire intelligent pour les architectes
Conforme à la réglementation française d'urbanisme 2025
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

from config import Config
from utils import validate_project_data, get_nested_value

logger = logging.getLogger('ArchiBot.intelligent_form')

class TypeProjet(Enum):
    """Types de projets selon la réglementation française"""
    CONSTRUCTION_NEUVE = "construction_neuve"
    EXTENSION = "extension"
    RENOVATION = "renovation"
    AMENAGEMENT = "amenagement"
    MODIFICATION = "modification"
    TRANSFERT = "transfert"
    DEMOLITION = "demolition"
    APPEL_OFFRES_PUBLIC = "appel_offres_public"

class DestinationBatiment(Enum):
    """Destinations selon le code de l'urbanisme"""
    HABITATION = "habitation"
    COMMERCE = "commerce"
    ARTISANAT = "artisanat"
    INDUSTRIE = "industrie"
    EXPLOITATION_AGRICOLE = "exploitation_agricole"
    ENTREPOT = "entrepot"
    BUREAU = "bureau"
    SERVICE_PUBLIC = "service_public"
    ERP = "erp"  # Établissement Recevant du Public
    AUTRE = "autre"

class ZoneUrbanisme(Enum):
    """Zones PLU selon le code de l'urbanisme"""
    ZONE_U = "zone_u"  # Zone urbaine
    ZONE_AU = "zone_au"  # Zone à urbaniser
    ZONE_A = "zone_a"  # Zone agricole
    ZONE_N = "zone_n"  # Zone naturelle

@dataclass
class ContexteReglementaire:
    """Contexte réglementaire pour la prise de décision"""
    zone_plu: ZoneUrbanisme
    secteur_sauvegarde: bool = False
    zone_abf: bool = False  # Architecte des Bâtiments de France
    site_classe: bool = False
    site_inscrit: bool = False
    zone_inondable: bool = False
    servitude_utilite_publique: bool = False
    commune_plus_3500_hab: bool = True
    dtu_applicable: str = "RE2020"  # RT2012, RE2020

@dataclass
class ArchitecteInfo:
    """Informations de l'architecte conforme à la réglementation"""
    nom: str
    prenom: str
    numero_ordre: str  # Obligatoire
    numero_assurance: str  # RC Pro obligatoire
    adresse_agence: str
    telephone: str
    email: str
    qualifications: List[str]  # OPQIBI, etc.
    date_inscription_ordre: str

class IntelligentFormSystem:
    """Système de formulaire intelligent pour architectes"""
    
    def __init__(self):
        """Initialise le système avec les règles métier françaises"""
        self.regles_urbanisme = self._charger_regles_urbanisme()
        self.seuils_reglementaires = self._charger_seuils_reglementaires()
        self.templates_projets = self._charger_templates_projets()
        
    def _charger_regles_urbanisme(self) -> Dict[str, Any]:
        """Charge les règles d'urbanisme françaises"""
        return {
            # Article R*421-1 et suivants du Code de l'urbanisme
            "seuils_permis_construire": {
                "personne_physique": {
                    "surface_plancher": 150,  # m²
                    "emprise_sol": 150  # m²
                },
                "personne_morale": {
                    "surface_plancher": 0,  # Toujours PC
                    "emprise_sol": 0
                }
            },
            "seuils_declaration_prealable": {
                "extension": {
                    "zone_urbaine": {"min": 5, "max": 40},  # m²
                    "zone_protegee": {"min": 0, "max": 20}  # m²
                },
                "modification_aspect": True,
                "construction_annexe": {"max": 20}  # m²
            },
            "obligations_architecte": {
                "surface_plancher_min": 150,  # m²
                "emprise_sol_min": 150,  # m²
                "personne_morale": True,
                "erp": True,
                "batiment_france": True
            },
            "delais_instruction": {
                "permis_construire_maison": 60,  # jours
                "permis_construire_autre": 90,
                "declaration_prealable": 30,
                "permis_amenager": 90,
                "permis_demolir": 60,
                "modificatif": 60,
                "transfert": 30,
                "certificat_urbanisme": 30
            }
        }
    
    def _charger_seuils_reglementaires(self) -> Dict[str, Any]:
        """Charge les seuils réglementaires 2025"""
        return {
            "etude_thermique": {
                "surface_min": 50,  # m²
                "norme": "RE2020"
            },
            "etude_sol": {
                "surface_terrain_min": 1000,  # m²
                "zone_sensible": True
            },
            "raccordement_reseaux": {
                "assainissement_collectif": True,
                "eau_potable": True,
                "electricite": True
            },
            "accessibilite_pmr": {
                "erp": True,
                "logement_collectif": True,
                "seuil_logements": 3
            },
            "stationnement": {
                "ratio_logement": 1,  # places par logement
                "ratio_commerce": 1  # places par 25m²
            }
        }
    
    def _charger_templates_projets(self) -> Dict[str, Any]:
        """Templates de projets types pour les architectes"""
        return {
            "maison_individuelle": {
                "surface_type": 120,
                "emprise_type": 100,
                "hauteur_type": 8,
                "destination": DestinationBatiment.HABITATION,
                "documents_types": ["plans", "facades", "coupes", "notice"],
                "etudes_requises": ["thermique", "sol"]
            },
            "extension_maison": {
                "surface_type": 30,
                "rattachement_existant": True,
                "respect_prospect": True,
                "documents_types": ["plans", "facades", "notice"]
            },
            "renovation_batiment": {
                "changement_destination": False,
                "modification_structure": False,
                "isolation_thermique": True,
                "documents_types": ["etat_existant", "projet", "notice"]
            },
            "etablissement_commercial": {
                "surface_type": 200,
                "accessibilite_pmr": True,
                "stationnement": True,
                "etudes_requises": ["impact", "securite", "accessibilite"]
            }
        }
    
    def analyser_projet(self, donnees_projet: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse intelligente d'un projet selon la réglementation"""
        logger.info("Début analyse projet intelligent")
        
        # Extraction des données
        client = donnees_projet.get('client', {})
        projet = donnees_projet.get('projet', {})
        technique = donnees_projet.get('technique', {})
        
        # Détermination du statut juridique
        est_personne_physique = not client.get('numeroSiret')
        
        # Calculs réglementaires
        surface_plancher = float(projet.get('surfacePlancher', 0))
        emprise_sol = float(projet.get('empriseSol', surface_plancher * 0.8))  # Estimation
        surface_terrain = float(projet.get('surfaceTerrain', 0))
        
        # Analyse du contexte réglementaire
        contexte = self._analyser_contexte_reglementaire(projet, technique)
        
        # Détermination des autorisations nécessaires
        autorisations = self._determiner_autorisations(
            projet, surface_plancher, emprise_sol, est_personne_physique, contexte
        )
        
        # Vérification des obligations
        obligations = self._verifier_obligations(
            surface_plancher, emprise_sol, est_personne_physique, 
            projet.get('destination'), contexte
        )
        
        # Calcul des délais
        delais = self._calculer_delais_instruction(autorisations, contexte)
        
        # Recommandations techniques
        recommandations = self._generer_recommandations(
            projet, surface_plancher, surface_terrain, contexte
        )
        
        # Alertes réglementaires
        alertes = self._generer_alertes_reglementaires(
            obligations, contexte, surface_plancher, est_personne_physique
        )
        
        return {
            'autorisations_requises': autorisations,
            'obligations_reglementaires': obligations,
            'delais_instruction': delais,
            'recommandations_techniques': recommandations,
            'alertes_conformite': alertes,
            'contexte_reglementaire': asdict(contexte),
            'resume_analyse': self._generer_resume_analyse(
                autorisations, obligations, delais, alertes
            )
        }
    
    def _analyser_contexte_reglementaire(self, projet: Dict, technique: Dict) -> ContexteReglementaire:
        """Analyse le contexte réglementaire du projet"""
        return ContexteReglementaire(
            zone_plu=ZoneUrbanisme.ZONE_U,  # Par défaut, à déterminer avec API PLU
            zone_abf=technique.get('zoneProtegee', False),
            secteur_sauvegarde=technique.get('secteurSauvegarde', False),
            site_classe=technique.get('siteClasse', False),
            commune_plus_3500_hab=self._determiner_taille_commune(projet.get('codePostalProjet'))
        )
    
    def _determiner_autorisations(self, projet: Dict, surface_plancher: float, 
                                 emprise_sol: float, est_personne_physique: bool,
                                 contexte: ContexteReglementaire) -> List[Dict[str, Any]]:
        """Détermine les autorisations d'urbanisme requises"""
        autorisations = []
        type_projet = projet.get('typeProjet')
        
        if type_projet == TypeProjet.CONSTRUCTION_NEUVE.value:
            if est_personne_physique and surface_plancher <= 150 and emprise_sol <= 150:
                autorisations.append({
                    'type': 'CERFA 13406*15',
                    'nom': 'Permis de construire pour une maison individuelle',
                    'article_code': 'R*421-1',
                    'obligatoire': True,
                    'delai_instruction': 60,
                    'pieces_jointes': self._pieces_pc_maison_individuelle()
                })
            else:
                autorisations.append({
                    'type': 'CERFA 13409*15', 
                    'nom': 'Permis de construire',
                    'article_code': 'R*421-1',
                    'obligatoire': True,
                    'delai_instruction': 90,
                    'pieces_jointes': self._pieces_pc_autre()
                })
        
        elif type_projet == TypeProjet.EXTENSION.value:
            if surface_plancher <= 20 and not contexte.zone_abf:
                # Extension sans autorisation si < 5m² et pas en zone protégée
                if surface_plancher >= 5:
                    autorisations.append({
                        'type': 'CERFA 16702*01',
                        'nom': 'Déclaration préalable - Extension',
                        'article_code': 'R*421-9',
                        'obligatoire': True,
                        'delai_instruction': 30
                    })
            elif surface_plancher <= 40:
                autorisations.append({
                    'type': 'CERFA 16702*01',
                    'nom': 'Déclaration préalable - Extension',
                    'article_code': 'R*421-9',
                    'obligatoire': True,
                    'delai_instruction': 30
                })
            else:
                # Extension > 40m² = Permis de construire
                if est_personne_physique:
                    autorisations.append({
                        'type': 'CERFA 13406*15',
                        'nom': 'Permis de construire maison - Extension',
                        'article_code': 'R*421-1',
                        'obligatoire': True,
                        'delai_instruction': 60
                    })
                else:
                    autorisations.append({
                        'type': 'CERFA 13409*15',
                        'nom': 'Permis de construire - Extension',
                        'article_code': 'R*421-1',
                        'obligatoire': True,
                        'delai_instruction': 90
                    })
        
        # Toujours proposer le certificat d'urbanisme
        autorisations.append({
            'type': 'CERFA 13410*12',
            'nom': 'Certificat d\'urbanisme opérationnel',
            'article_code': 'R*410-1',
            'obligatoire': False,
            'recommande': True,
            'delai_instruction': 30,
            'utilite': 'Connaître les règles d\'urbanisme et la faisabilité'
        })
        
        return autorisations
    
    def _verifier_obligations(self, surface_plancher: float, emprise_sol: float,
                            est_personne_physique: bool, destination: str,
                            contexte: ContexteReglementaire) -> Dict[str, Any]:
        """Vérifie les obligations réglementaires"""
        obligations = {
            'architecte': False,
            'etude_thermique': False,
            'etude_impact': False,
            'etude_sol': False,
            'accessibilite_pmr': False,
            'dematerialisation': False
        }
        
        # Obligation architecte (Article L431-3)
        if (surface_plancher > 150 or emprise_sol > 150 or 
            not est_personne_physique or 
            destination == DestinationBatiment.ERP.value or
            contexte.zone_abf):
            obligations['architecte'] = True
        
        # Étude thermique (RE2020)
        if surface_plancher > 50:
            obligations['etude_thermique'] = True
        
        # Étude de sol (Article L132-3)
        if surface_plancher > 100:  # Construction en zone sismique
            obligations['etude_sol'] = True
        
        # Accessibilité PMR
        if destination == DestinationBatiment.ERP.value:
            obligations['accessibilite_pmr'] = True
        
        # Dématérialisation obligatoire
        if not est_personne_physique and contexte.commune_plus_3500_hab:
            obligations['dematerialisation'] = True
        
        return obligations
    
    def _calculer_delais_instruction(self, autorisations: List[Dict], 
                                   contexte: ContexteReglementaire) -> Dict[str, Any]:
        """Calcule les délais d'instruction"""
        delai_max = 30
        for auth in autorisations:
            if auth.get('obligatoire'):
                delai_max = max(delai_max, auth.get('delai_instruction', 30))
        
        # Majoration ABF
        if contexte.zone_abf:
            delai_max += 15
        
        # Date de dépôt recommandée
        date_depot_recommandee = datetime.now() + timedelta(days=delai_max + 30)
        
        return {
            'delai_instruction_max': delai_max,
            'delai_avec_majorations': delai_max,
            'date_depot_recommandee': date_depot_recommandee.strftime('%Y-%m-%d'),
            'planning_recommande': self._generer_planning_projet(delai_max)
        }
    
    def _generer_recommandations(self, projet: Dict, surface_plancher: float,
                               surface_terrain: float, contexte: ContexteReglementaire) -> List[str]:
        """Génère des recommandations techniques"""
        recommandations = []
        
        if surface_plancher > 100:
            recommandations.append("Prévoir une étude géotechnique G2 avant conception")
        
        if contexte.zone_abf:
            recommandations.append("Consulter l'ABF en amont pour validation du projet")
        
        if surface_plancher > 1000:
            recommandations.append("Étude d'impact environnemental requise")
        
        if projet.get('destination') == DestinationBatiment.ERP.value:
            recommandations.append("Consultation commission sécurité incendie")
            recommandations.append("Dossier accessibilité PMR obligatoire")
        
        recommandations.append("Vérifier la conformité RE2020 dès l'esquisse")
        recommandations.append("Anticiper les réseaux et raccordements")
        
        return recommandations
    
    def _generer_alertes_reglementaires(self, obligations: Dict, contexte: ContexteReglementaire,
                                      surface_plancher: float, est_personne_physique: bool) -> List[Dict]:
        """Génère les alertes de conformité réglementaire"""
        alertes = []
        
        if obligations['architecte']:
            alertes.append({
                'niveau': 'obligation',
                'type': 'architecte_obligatoire',
                'message': '⚠️ Recours à un architecte obligatoire',
                'article': 'Article L431-3 du Code de l\'urbanisme'
            })
        
        if obligations['dematerialisation']:
            alertes.append({
                'niveau': 'obligation',
                'type': 'dematerialisation',
                'message': '💻 Dépôt dématérialisé obligatoire',
                'article': 'Article L423-3 du Code de l\'urbanisme'
            })
        
        if contexte.zone_abf:
            alertes.append({
                'niveau': 'information',
                'type': 'abf',
                'message': '🏛️ Avis ABF requis (+15 jours d\'instruction)',
                'article': 'Article L621-31 du Code du patrimoine'
            })
        
        if surface_plancher > 170:
            alertes.append({
                'niveau': 'information', 
                'type': 'seuil_bat',
                'message': '🏗️ Seuil Bâtiments de France dépassé (170m²)',
                'article': 'Code de l\'urbanisme'
            })
        
        return alertes
    
    def _pieces_pc_maison_individuelle(self) -> List[str]:
        """Liste des pièces pour PC maison individuelle"""
        return [
            "PC1 - Plan de situation",
            "PC2 - Plan de masse",
            "PC3 - Plan en coupe du terrain",
            "PC4 - Notice descriptive",
            "PC5 - Plans des façades et toitures",
            "PC6 - Document graphique (perspectives)",
            "PC7 - Photographies du terrain",
            "PC8 - Document d'insertion paysagère"
        ]
    
    def _pieces_pc_autre(self) -> List[str]:
        """Liste des pièces pour PC autre"""
        return [
            "PC1 - Plan de situation", 
            "PC2 - Plan de masse",
            "PC3 - Plan en coupe du terrain",
            "PC4 - Notice descriptive",
            "PC5 - Plans des façades et toitures", 
            "PC6 - Document graphique",
            "PC7 - Photographies du terrain",
            "PC11 - Notice accessibilité",
            "PC12 - Étude d'impact (si requis)"
        ]
    
    def _determiner_taille_commune(self, code_postal: str) -> bool:
        """Détermine si la commune fait plus de 3500 habitants"""
        # Simplification - en réalité, consulter base INSEE
        grandes_communes = ['75', '69', '13', '33', '31', '59', '92', '93', '94']
        return any(code_postal.startswith(prefix) for prefix in grandes_communes)
    
    def _generer_planning_projet(self, delai_instruction: int) -> List[Dict[str, str]]:
        """Génère un planning type de projet"""
        today = datetime.now()
        return [
            {
                'phase': 'Études préalables',
                'duree': '4-8 semaines',
                'date_debut': today.strftime('%Y-%m-%d')
            },
            {
                'phase': 'Constitution dossier',
                'duree': '2-4 semaines', 
                'date_debut': (today + timedelta(weeks=6)).strftime('%Y-%m-%d')
            },
            {
                'phase': 'Dépôt et instruction',
                'duree': f'{delai_instruction} jours',
                'date_debut': (today + timedelta(weeks=10)).strftime('%Y-%m-%d')
            },
            {
                'phase': 'Début travaux',
                'duree': 'Après autorisation',
                'date_debut': (today + timedelta(days=delai_instruction + 70)).strftime('%Y-%m-%d')
            }
        ]
    
    def _generer_resume_analyse(self, autorisations: List, obligations: Dict,
                              delais: Dict, alertes: List) -> Dict[str, Any]:
        """Génère un résumé de l'analyse"""
        nb_autorisations_obligatoires = len([a for a in autorisations if a.get('obligatoire')])
        nb_obligations = len([k for k, v in obligations.items() if v])
        niveau_complexite = self._evaluer_complexite(nb_autorisations_obligatoires, nb_obligations, len(alertes))
        
        return {
            'nombre_autorisations': len(autorisations),
            'nombre_obligations': nb_obligations,
            'delai_total_estime': delais['delai_instruction_max'],
            'niveau_complexite': niveau_complexite,
            'conformite_reglementaire': len([a for a in alertes if a['niveau'] == 'obligation']) == 0,
            'recommandation_globale': self._recommandation_globale(niveau_complexite, nb_obligations)
        }
    
    def _evaluer_complexite(self, nb_auth: int, nb_obligations: int, nb_alertes: int) -> str:
        """Évalue la complexité du projet"""
        score = nb_auth + nb_obligations + (nb_alertes * 0.5)
        if score <= 3:
            return "Simple"
        elif score <= 6:
            return "Modérée"
        else:
            return "Complexe"
    
    def _recommandation_globale(self, complexite: str, nb_obligations: int) -> str:
        """Recommandation globale selon la complexité"""
        if complexite == "Simple":
            return "Projet standard - Dossier réalisable en interne"
        elif complexite == "Modérée":
            return "Projet nécessitant une expertise - Prévoir 2-3 mois"
        else:
            return "Projet complexe - Recours à des experts spécialisés recommandé"

# Fonctions utilitaires pour l'interface
def generer_formulaire_intelligent(donnees_partielles: Dict[str, Any]) -> Dict[str, Any]:
    """Génère un formulaire intelligent basé sur les données partielles"""
    system = IntelligentFormSystem()
    
    # Analyse avec les données disponibles
    if donnees_partielles.get('projet', {}).get('typeProjet'):
        analyse = system.analyser_projet(donnees_partielles)
    else:
        analyse = {'autorisations_requises': [], 'alertes_conformite': []}
    
    # Suggestions de saisie
    suggestions = _generer_suggestions_saisie(donnees_partielles)
    
    # Validation en temps réel
    erreurs_validation = validate_project_data(donnees_partielles)
    
    return {
        'analyse_reglementaire': analyse,
        'suggestions_saisie': suggestions,
        'erreurs_validation': erreurs_validation,
        'completion_rate': _calculer_taux_completion(donnees_partielles)
    }

def _generer_suggestions_saisie(donnees: Dict) -> List[Dict]:
    """Génère des suggestions de saisie intelligentes"""
    suggestions = []
    
    projet = donnees.get('projet', {})
    
    if projet.get('typeProjet') == 'extension':
        suggestions.append({
            'champ': 'surfacePlancher',
            'suggestion': 'Pour une extension, surface généralement entre 15-40m²',
            'valeur_typique': 25
        })
    
    if projet.get('destination') == 'habitation':
        suggestions.append({
            'champ': 'surfaceTerrain',
            'suggestion': 'Terrain habitation type: 400-800m²',
            'valeur_typique': 600
        })
    
    return suggestions

def _calculer_taux_completion(donnees: Dict) -> int:
    """Calcule le taux de completion intelligent"""
    champs_obligatoires = [
        'client.nom', 'client.prenom', 'client.adresse',
        'projet.typeProjet', 'projet.adresseProjet'
    ]
    
    champs_remplis = 0
    for chemin in champs_obligatoires:
        if get_nested_value(donnees, chemin):
            champs_remplis += 1
    
    return int((champs_remplis / len(champs_obligatoires)) * 100)