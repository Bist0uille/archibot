"""
Utilitaires pour la validation des données et la gestion des ressources
"""

import re
import logging
from contextlib import contextmanager
from config import Config

logger = logging.getLogger('ArchiBot.utils')

def validate_postal_code(code):
    """Valide un code postal français (5 chiffres)."""
    if not code:
        return False
    return bool(re.match(Config.VALIDATION_PATTERNS['postal_code'], str(code).strip()))

def validate_siret(siret):
    """Valide un numéro SIRET (14 chiffres)."""
    if not siret:
        return True  # SIRET optionnel
    cleaned_siret = str(siret).replace(' ', '').replace('-', '')
    return bool(re.match(Config.VALIDATION_PATTERNS['siret'], cleaned_siret))

def validate_email(email):
    """Valide une adresse email."""
    if not email:
        return True  # Email optionnel
    return bool(re.match(Config.VALIDATION_PATTERNS['email'], str(email).strip()))

def validate_date(date_str):
    """Valide une date au format YYYY-MM-DD."""
    if not date_str:
        return True  # Date optionnelle
    return bool(re.match(Config.VALIDATION_PATTERNS['date'], str(date_str).strip()))

def validate_numeric_field(value, field_name="champ"):
    """Valide qu'un champ numérique est bien un nombre positif."""
    if not value:
        return True  # Champ optionnel
    try:
        num_value = float(str(value).strip())
        if num_value < 0:
            logger.warning(f"Valeur négative détectée pour {field_name}: {num_value}")
            return False
        return True
    except ValueError:
        logger.error(f"Valeur non numérique pour {field_name}: {value}")
        return False

def validate_project_data(project_data):
    """Valide les données d'un projet."""
    errors = []
    
    # Validation du client
    client = project_data.get('client', {})
    
    if not client.get('nom'):
        errors.append("Le nom du client est obligatoire")
    
    if not client.get('prenom'):
        errors.append("Le prénom du client est obligatoire")
    
    if not client.get('adresse'):
        errors.append("L'adresse du client est obligatoire")
    
    if client.get('codePostal') and not validate_postal_code(client['codePostal']):
        errors.append("Code postal invalide (doit être 5 chiffres)")
    
    if not client.get('ville'):
        errors.append("La ville du client est obligatoire")
    
    if client.get('email') and not validate_email(client['email']):
        errors.append("Adresse email invalide")
    
    if client.get('numeroSiret') and not validate_siret(client['numeroSiret']):
        errors.append("Numéro SIRET invalide (doit être 14 chiffres)")
    
    if client.get('dateNaissance') and not validate_date(client['dateNaissance']):
        errors.append("Date de naissance invalide (format YYYY-MM-DD)")
    
    # Validation du projet
    projet = project_data.get('projet', {})
    
    if not projet.get('typeProjet'):
        errors.append("Le type de projet est obligatoire")
    
    if not projet.get('adresseProjet'):
        errors.append("L'adresse du projet est obligatoire")
    
    if projet.get('surfaceTerrain') and not validate_numeric_field(projet['surfaceTerrain'], "surface terrain"):
        errors.append("Surface terrain invalide")
    
    if projet.get('surfacePlancher') and not validate_numeric_field(projet['surfacePlancher'], "surface plancher"):
        errors.append("Surface plancher invalide")
    
    if projet.get('hauteurBatiment') and not validate_numeric_field(projet['hauteurBatiment'], "hauteur bâtiment"):
        errors.append("Hauteur bâtiment invalide")
    
    if projet.get('nombreNiveaux') and not validate_numeric_field(projet['nombreNiveaux'], "nombre de niveaux"):
        errors.append("Nombre de niveaux invalide")
    
    if projet.get('dateDepotSouhaitee') and not validate_date(projet['dateDepotSouhaitee']):
        errors.append("Date de dépôt souhaitée invalide (format YYYY-MM-DD)")
    
    return errors

@contextmanager
def safe_pdf_context(pdf_path):
    """Context manager pour gérer les ressources PDF en toute sécurité."""
    import fitz
    doc = None
    try:
        doc = fitz.open(pdf_path)
        yield doc
    except Exception as e:
        logger.error(f"Erreur lors de l'ouverture du PDF {pdf_path}: {e}")
        raise
    finally:
        if doc:
            doc.close()
            logger.debug(f"PDF fermé: {pdf_path}")

def get_nested_value(data_dict, key_path, default=None):
    """Récupère une valeur dans un dictionnaire imbriqué via un chemin (ex: 'societe.adresse.ville')."""
    if not key_path:
        return default
        
    keys = key_path.split('.')
    value = data_dict
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value if value is not None else default

def sanitize_filename(filename):
    """Nettoie un nom de fichier en supprimant les caractères interdits."""
    # Remplace les caractères interdits par des underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Supprime les espaces en début/fin
    sanitized = sanitized.strip()
    # Limite la longueur
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized