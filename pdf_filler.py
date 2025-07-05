import fitz  # PyMuPDF
import json
from pathlib import Path
from cerfa_field_mappings import CERFA_FIELD_MAPPINGS
from config import Config

# Dictionnaire de correspondance pour les infos de l'architecte
ARCHITECT_INTERNAL_MAP = {
    "architecte.nom": "H1N_nom",
    "architecte.prenom": "H1P_prenom",
    "architecte.email": "H1AE1_email",
    "architecte.telephone": "H1T_telephone",
    "societe.raison_sociale": "H2R_raison",
    "societe.siret": "H2S_siret",
    "societe.adresse.numero": "H1Q_numero",
    "societe.adresse.voie": "H1V_voie",
    "societe.adresse.code_postal": "H1C_code",
    "societe.adresse.ville": "H1L_localite",
    "ordre_architectes.numero_national": "H1K_ordre",
    "ordre_architectes.conseil_regional": "H1R_conseil",
}

def get_nested_value(data_dict, key_path):
    """Récupère une valeur dans un dictionnaire imbriqué via un chemin (ex: 'societe.adresse.ville')."""
    keys = key_path.split('.')
    value = data_dict
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value

def fill_pdf(cerfa_id: str, project_data_dict: dict, output_pdf_path: str):
    """
    Remplit un formulaire PDF en fusionnant les données de l'architecte et celles du projet.

    Args:
        cerfa_id (str): L'identifiant du CERFA (ex: '13406-15').
        project_data_dict (dict): Dictionnaire des données du projet (client, projet, technique).
        output_pdf_path (str): Chemin absolu où le PDF rempli doit être sauvegardé.
    """
    
    template_pdf_path = Config.CERFA_TEMPLATES_DIR / f"cerfa_{cerfa_id}.pdf"
    architect_info_path = Config.ARCHITECT_INFO_PATH

    try:
        # 1. Charger les données de l'architecte
        with open(architect_info_path, 'r', encoding='utf-8') as f:
            architect_data = json.load(f)

        # 2. Préparer les données en pré-remplissant avec les infos de l'architecte
        final_data = {}
        for generic_key, cerfa_field in ARCHITECT_INTERNAL_MAP.items():
            value = get_nested_value(architect_data, generic_key)
            if value:
                final_data[cerfa_field] = value

        # 3. Appliquer les données du projet par-dessus, en utilisant le mappage spécifique au CERFA
        cerfa_mapping = CERFA_FIELD_MAPPINGS.get(cerfa_id)
        if not cerfa_mapping:
            print(f"Avertissement : Aucun mappage trouvé pour le CERFA {cerfa_id}. Seules les infos de l'architecte seront utilisées.")
        else:
            for generic_key, cerfa_field in cerfa_mapping.items():
                if not cerfa_field:
                    continue

                value = get_nested_value(project_data_dict, generic_key)
                if value is None or value == "":
                    continue

                # --- GESTION DES CAS SPÉCIFIQUES ---
                # Si le mapping est un dictionnaire, on traite un groupe de cases à cocher/options
                if isinstance(cerfa_field, dict):
                    if value in cerfa_field and cerfa_field[value]:
                        final_data[cerfa_field[value]] = "On"  # Valeur standard pour cocher
                
                # Si le champ est une date à décomposer (logique simplifiée)
                elif "date" in generic_key.lower() and isinstance(value, str) and '-' in value:
                    try:
                        parts = value.split('-')
                        if len(parts) == 3 and cerfa_mapping.get(f"{generic_key}.jour"):
                            final_data[cerfa_mapping[f"{generic_key}.jour"]] = parts[2]
                            final_data[cerfa_mapping[f"{generic_key}.mois"]] = parts[1]
                            final_data[cerfa_mapping[f"{generic_key}.annee"]] = parts[0]
                        else:
                            final_data[cerfa_field] = value # Fallback si pas de mapping jour/mois/année
                    except Exception:
                        final_data[cerfa_field] = value
                
                # Cas général pour les champs texte simples
                else:
                    final_data[cerfa_field] = value
        
        # 4. Ouvrir le modèle PDF
        doc = fitz.open(template_pdf_path)

        # 5. Remplir les champs
        filled_count = 0
        for page in doc:
            for field in page.widgets():
                field_name = field.field_name
                if field_name in final_data and final_data[field_name] is not None:
                    try:
                        field.field_value = str(final_data[field_name])
                        field.update()
                        filled_count += 1
                    except Exception as e:
                        print(f"Impossible de définir la valeur pour le champ {field_name}: {e}")
        
        print(f"{filled_count} champs ont été remplis pour le CERFA {cerfa_id}.")

        # 6. Sauvegarder le PDF rempli
        doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
        print(f"Succès ! Fichier de sortie créé : {output_pdf_path}")

    except FileNotFoundError as e:
        print(f"Erreur : Fichier introuvable. Vérifiez les chemins : {e.filename}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
