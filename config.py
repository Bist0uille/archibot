"""
Configuration centralisée pour l'application ArchiBot - Remplisseur de CERFA
"""

import os
from pathlib import Path
import logging

class Config:
    """Configuration centralisée pour l'application."""
    
    # Chemins de base
    BASE_DIR = Path(__file__).parent
    
    # Répertoires de données
    CERFA_TEMPLATES_DIR = BASE_DIR / 'cerfa_templates'
    CERFA_DATA_DIR = BASE_DIR / 'cerfa_data'
    FILLED_PDFS_DIR = BASE_DIR / 'filled_pdfs'
    
    # Fichiers de configuration
    ARCHITECT_INFO_PATH = BASE_DIR / 'mes_infos_cecile.json'
    
    # Configuration des logs
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Validation des données
    VALIDATION_PATTERNS = {
        'postal_code': r'^\d{5}$',
        'siret': r'^\d{14}$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'date': r'^\d{4}-\d{2}-\d{2}$'
    }
    
    # Configuration PDF
    PDF_COMPRESSION_SETTINGS = {
        'garbage': 4,
        'deflate': True,
        'clean': True
    }
    
    @classmethod
    def ensure_directories(cls):
        """Crée les répertoires nécessaires s'ils n'existent pas."""
        directories = [
            cls.CERFA_TEMPLATES_DIR,
            cls.CERFA_DATA_DIR,
            cls.FILLED_PDFS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def setup_logging(cls):
        """Configure le système de logging."""
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.BASE_DIR / 'archibot.log'),
                logging.StreamHandler()
            ]
        )
        
        # Créer un logger pour l'application
        return logging.getLogger('ArchiBot')