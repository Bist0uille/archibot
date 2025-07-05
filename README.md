# ArchiBot - Assistant Intelligent pour Architectes

**ArchiBot** est une application de bureau conçue pour assister les architectes dans la gestion administrative de leurs projets. Elle automatise la sélection et le pré-remplissage des formulaires CERFA en fonction des spécificités de chaque projet, tout en fournissant des alertes réglementaires en temps réel.

## ✨ Fonctionnalités Principales

- **Assistant de Saisie Intelligent** : Une interface graphique guide l'utilisateur à travers plusieurs étapes pour collecter les informations du client, du projet et les détails techniques.
- **Analyse Réglementaire Automatisée** : Le cœur de l'application analyse les données saisies pour :
  - **Déterminer les CERFA requis** : Identifie automatiquement les formulaires obligatoires et optionnels (Permis de Construire, Déclaration Préalable, etc.) selon un ensemble de règles métier précises (type de projet, surface, nature du client).
  - **Générer des Alertes de Conformité** : Prévient l'utilisateur sur des points de vigilance critiques comme l'obligation de recourir à un architecte, la nécessité d'études spécifiques (thermique, sol), ou les contraintes liées aux zones protégées (ABF).
  - **Estimer les Délais** : Calcule le délai d'instruction administratif en fonction des documents à produire.
- **Remplissage Automatique de PDF** : Génère les formulaires CERFA sélectionnés en les remplissant automatiquement avec les données du projet et les informations pré-enregistrées de l'architecte.
- **Gestion de Projet** : Permet de sauvegarder et de charger des projets en cours au format JSON.

## 🚀 Démarrage Rapide

Pour lancer l'application, assurez-vous que les dépendances Python nécessaires sont installées, puis exécutez le script principal :

```bash
# Naviguez vers le dossier de l'application
cd pdffiller_v0

# Lancez l'interface graphique
python intelligent_interface.py
```

## 📂 Structure du Projet

- `intelligent_interface.py` : Point d'entrée de l'application, gère l'interface utilisateur (GUI) avec Tkinter.
- `architect_business_logic.py` : Le "cerveau" de l'application. Contient toute la logique métier pour l'analyse des projets et la sélection des CERFA.
- `pdf_filler.py` : Gère la lecture des modèles PDF et le remplissage des champs.
- `cerfa_field_mappings.py` : Dictionnaire de correspondance entre les données génériques du projet et les noms des champs spécifiques à chaque PDF.
- `config.py` : Fichier de configuration central pour les chemins et autres paramètres.
- `mes_infos_cecile.json` : Fichier de données contenant les informations de l'architecte à pré-remplir.
- `/cerfa_templates/` : Dossier contenant les modèles de formulaires CERFA au format PDF.
- `/filled_pdfs/` : Dossier où les PDF remplis sont sauvegardés.
- `/cerfa_data/` : Dossier où les projets sauvegardés sont stockés.