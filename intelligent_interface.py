"""
Interface utilisateur intelligente et progressive
Optimisée pour le workflow des architectes
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Imports locaux
sys.path.append(str(Path(__file__).parent))
from config import Config
from architect_business_logic import ArchitectBusinessLogic
from utils import validate_project_data
from pdf_filler import fill_pdf

class ProgressiveFormWizard:
    """Assistant de saisie progressive et intelligente"""
    
    def __init__(self, master):
        self.master = master
        self.master.title("ArchiBot - Assistant Intelligent CERFA 2025")
        self.master.geometry("1200x800")
        self.master.configure(bg='#f8f9fa')
        
        # Système intelligent
        self.architect_logic = ArchitectBusinessLogic()
        
        # Données du projet
        self.project_data = {
            'client': {}, 'projet': {}, 'technique': {},
            'mission': {'type': 'permis_construire', 'phase_actuelle': 'avant_projet'}
        }
        
        # État de l'interface
        self.current_step = 0
        self.completion_rate = 0
        self.suggestions_active = True
        self.auto_analysis = True
        
        # Configuration des étapes
        self.steps = [
            {"name": "Type de Projet", "icon": "🏗️", "fields": ["typeProjet", "destination"]},
            {"name": "Client", "icon": "👥", "fields": ["nom", "prenom", "adresse"]},
            {"name": "Projet", "icon": "📐", "fields": ["adresseProjet", "surfacePlancher", "surfaceTerrain"]},
            {"name": "Technique", "icon": "⚙️", "fields": ["zoneProtegee", "demolition"]},
            {"name": "Mission", "icon": "📋", "fields": ["typeMission", "planning"]},
            {"name": "Validation", "icon": "✅", "fields": []}
        ]
        
        self._create_interface()
        self._setup_auto_completion()
        
    def _create_interface(self):
        """Crée l'interface principale"""
        # Style ttk personnalisé
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des couleurs
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), background='#f8f9fa')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), background='#f8f9fa', foreground='#6c757d')
        style.configure('Step.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        
        # Header principal
        self._create_header()
        
        # Zone principale avec sidebar + contenu
        main_frame = tk.Frame(self.master, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sidebar avec progression
        self._create_sidebar(main_frame)
        
        # Zone de contenu principal
        self._create_content_area(main_frame)
        
        # Zone d'analyse en temps réel
        self._create_analysis_panel(main_frame)
        
        # Footer avec navigation
        self._create_footer()
        
    def _create_header(self):
        """Crée l'en-tête avec titre et progression globale"""
        header_frame = tk.Frame(self.master, bg='#ffffff', height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20,0))
        header_frame.pack_propagate(False)
        
        # Titre principal
        title_frame = tk.Frame(header_frame, bg='#ffffff')
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=15)
        
        ttk.Label(title_frame, text="🏗️ ArchiBot Assistant", 
                 style='Title.TLabel', background='#ffffff').pack(anchor=tk.W)
        ttk.Label(title_frame, text="Assistant intelligent pour dossiers d'urbanisme", 
                 style='Subtitle.TLabel', background='#ffffff').pack(anchor=tk.W)
        
        # Indicateurs de progression
        progress_frame = tk.Frame(header_frame, bg='#ffffff')
        progress_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=15)
        
        self.completion_label = ttk.Label(progress_frame, text="0%", 
                                        font=('Segoe UI', 24, 'bold'), 
                                        foreground='#007bff', background='#ffffff')
        self.completion_label.pack()
        
        ttk.Label(progress_frame, text="Complété", 
                 style='Subtitle.TLabel', background='#ffffff').pack()
        
        # Barre de progression
        self.progress_bar = ttk.Progressbar(header_frame, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.BOTTOM, padx=20, pady=(0,10))
        
    def _create_sidebar(self, parent):
        """Crée la sidebar avec les étapes"""
        sidebar_frame = tk.Frame(parent, bg='#ffffff', width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,20))
        sidebar_frame.pack_propagate(False)
        
        # Titre sidebar
        ttk.Label(sidebar_frame, text="📋 Étapes du Projet", 
                 style='Step.TLabel', background='#ffffff').pack(pady=20, padx=20)
        
        # Liste des étapes
        self.step_frames = []
        for i, step in enumerate(self.steps):
            step_frame = self._create_step_widget(sidebar_frame, i, step)
            self.step_frames.append(step_frame)
        
        # Boutons d'action rapide
        self._create_quick_actions(sidebar_frame)
        
    def _create_step_widget(self, parent, index, step):
        """Crée un widget d'étape dans la sidebar"""
        step_frame = tk.Frame(parent, bg='#ffffff')
        step_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Indicateur d'étape
        indicator_frame = tk.Frame(step_frame, bg='#ffffff')
        indicator_frame.pack(side=tk.LEFT, padx=(0,10))
        
        # Cercle avec numéro/icône
        circle = tk.Canvas(indicator_frame, width=30, height=30, bg='#ffffff', highlightthickness=0)
        circle.pack()
        
        if index == self.current_step:
            color = '#007bff'
            text_color = 'white'
        elif index < self.current_step:
            color = '#28a745'
            text_color = 'white'
        else:
            color = '#e9ecef'
            text_color = '#6c757d'
        
        circle.create_oval(2, 2, 28, 28, fill=color, outline=color)
        circle.create_text(15, 15, text=str(index+1), fill=text_color, font=('Segoe UI', 10, 'bold'))
        
        # Texte de l'étape
        text_frame = tk.Frame(step_frame, bg='#ffffff')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        step_label = tk.Label(text_frame, text=f"{step['icon']} {step['name']}", 
                             bg='#ffffff', font=('Segoe UI', 10))
        step_label.pack(anchor=tk.W)
        
        # Clic pour navigation
        def go_to_step(s=index):
            if s <= self.current_step + 1:  # Autoriser seulement étape suivante ou précédente
                self.current_step = s
                self._update_content()
                self._update_sidebar()
        
        step_frame.bind("<Button-1>", lambda e: go_to_step())
        step_label.bind("<Button-1>", lambda e: go_to_step())
        
        return step_frame
    
    def _create_quick_actions(self, parent):
        """Crée les boutons d'action rapide"""
        actions_frame = tk.LabelFrame(parent, text="🚀 Actions Rapides", 
                                    bg='#ffffff', font=('Segoe UI', 9, 'bold'))
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Templates de projet
        ttk.Button(actions_frame, text="🏠 Maison 120m²", 
                  command=lambda: self._load_template('maison_120')).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="🔧 Extension 30m²", 
                  command=lambda: self._load_template('extension_30')).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="🏢 Rénovation", 
                  command=lambda: self._load_template('renovation')).pack(fill=tk.X, pady=2)
        
        # Actions système
        tk.Frame(actions_frame, height=10, bg='#ffffff').pack()
        ttk.Button(actions_frame, text="💾 Sauvegarder", 
                  command=self._save_project).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="📂 Charger", 
                  command=self._load_project).pack(fill=tk.X, pady=2)
        
    def _create_content_area(self, parent):
        """Crée la zone de contenu principal"""
        content_frame = tk.Frame(parent, bg='#f8f9fa')
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,20))
        
        # Zone de contenu scrollable
        canvas = tk.Canvas(content_frame, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self._update_content()
        
    def _create_analysis_panel(self, parent):
        """Crée le panneau d'analyse en temps réel"""
        analysis_frame = tk.Frame(parent, bg='#ffffff', width=300)
        analysis_frame.pack(side=tk.RIGHT, fill=tk.Y)
        analysis_frame.pack_propagate(False)
        
        # Titre
        ttk.Label(analysis_frame, text="📊 Analyse en Temps Réel", 
                 style='Step.TLabel', background='#ffffff').pack(pady=20, padx=20)
        
        # Zone d'analyse scrollable
        analysis_canvas = tk.Canvas(analysis_frame, bg='#ffffff')
        analysis_scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=analysis_canvas.yview)
        
        self.analysis_content = tk.Frame(analysis_canvas, bg='#ffffff')
        self.analysis_content.bind(
            "<Configure>",
            lambda e: analysis_canvas.configure(scrollregion=analysis_canvas.bbox("all"))
        )
        
        analysis_canvas.create_window((0, 0), window=self.analysis_content, anchor="nw")
        analysis_canvas.configure(yscrollcommand=analysis_scrollbar.set)
        
        analysis_canvas.pack(side="left", fill="both", expand=True, padx=20)
        analysis_scrollbar.pack(side="right", fill="y")
        
        self._update_analysis()
        
    def _create_footer(self):
        """Crée le footer avec navigation"""
        footer_frame = tk.Frame(self.master, bg='#ffffff', height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=(0,20))
        footer_frame.pack_propagate(False)
        
        # Boutons navigation
        nav_frame = tk.Frame(footer_frame, bg='#ffffff')
        nav_frame.pack(expand=True)
        
        self.prev_button = ttk.Button(nav_frame, text="← Précédent", 
                                    command=self._previous_step)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=15)
        
        self.next_button = ttk.Button(nav_frame, text="Suivant →", 
                                    command=self._next_step, style='Primary.TButton')
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=15)
        
        # Indicateur étape
        step_indicator = ttk.Label(nav_frame, 
                                 text=f"Étape {self.current_step + 1} sur {len(self.steps)}", 
                                 background='#ffffff')
        step_indicator.pack(pady=20)
        
    def _update_content(self):
        """Met à jour le contenu selon l'étape actuelle"""
        # Nettoyer le contenu existant
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        step = self.steps[self.current_step]
        
        # Titre de l'étape
        title_frame = tk.Frame(self.scrollable_frame, bg='#ffffff')
        title_frame.pack(fill=tk.X, pady=(0,20))
        
        ttk.Label(title_frame, text=f"{step['icon']} {step['name']}", 
                 style='Title.TLabel', background='#ffffff').pack(pady=20)
        
        # Contenu spécifique à l'étape
        if self.current_step == 0:
            self._create_project_type_step()
        elif self.current_step == 1:
            self._create_client_step()
        elif self.current_step == 2:
            self._create_project_step()
        elif self.current_step == 3:
            self._create_technical_step()
        elif self.current_step == 4:
            self._create_mission_step()
        elif self.current_step == 5:
            self._create_validation_step()
    
    def _create_project_type_step(self):
        """Crée l'étape de sélection du type de projet"""
        # Sélection type de projet
        type_frame = tk.LabelFrame(self.scrollable_frame, text="Type de Projet", 
                                 bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        type_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.type_var = tk.StringVar(value=self.project_data.get('projet', {}).get('typeProjet', ''))
        
        types_projets = [
            ("🏠 Construction neuve", "construction_neuve", "Création d'un nouveau bâtiment"),
            ("🔧 Extension", "extension", "Agrandissement d'un bâtiment existant"),
            ("🔨 Rénovation", "renovation", "Modification d'un bâtiment existant"),
            ("🌳 Aménagement", "amenagement", "Aménagement de terrain"),
            ("📝 Modification", "modification", "Modification d'une autorisation"),
            ("🏢 Appel d'offres public", "appel_offres_public", "Candidature marché public")
        ]
        
        for i, (label, value, description) in enumerate(types_projets):
            frame = tk.Frame(type_frame, bg='#ffffff')
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            rb = tk.Radiobutton(frame, text=label, variable=self.type_var, value=value,
                              bg='#ffffff', font=('Segoe UI', 10), 
                              command=self._on_type_change)
            rb.pack(side=tk.LEFT)
            
            desc_label = tk.Label(frame, text=description, bg='#ffffff', 
                                fg='#6c757d', font=('Segoe UI', 9))
            desc_label.pack(side=tk.LEFT, padx=(10,0))
        
        # Destination
        dest_frame = tk.LabelFrame(self.scrollable_frame, text="Destination du Bâtiment", 
                                 bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        dest_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.destination_var = tk.StringVar(value=self.project_data.get('projet', {}).get('destination', ''))
        
        destinations = [
            ("🏠 Habitation", "habitation"),
            ("🏪 Commerce", "commerce"),
            ("🏭 Industrie", "industrie"),
            ("🏛️ ERP", "erp"),
            ("🏢 Bureau", "bureau"),
            ("📦 Entrepôt", "entrepot")
        ]
        
        dest_grid = tk.Frame(dest_frame, bg='#ffffff')
        dest_grid.pack(padx=10, pady=10)
        
        for i, (label, value) in enumerate(destinations):
            rb = tk.Radiobutton(dest_grid, text=label, variable=self.destination_var, value=value,
                              bg='#ffffff', font=('Segoe UI', 10),
                              command=self._on_destination_change)
            rb.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
    
    def _create_client_step(self):
        """Crée l'étape des informations client"""
        client_frame = tk.LabelFrame(self.scrollable_frame, text="Informations Client", 
                                   bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        client_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Variables pour les champs client
        self.client_vars = {}
        client_fields = [
            ('civilite', 'Civilité', 'combobox', ['M.', 'Mme']),
            ('nom', 'Nom *', 'entry', None),
            ('prenom', 'Prénom *', 'entry', None),
            ('dateNaissance', 'Date de naissance', 'date', None),
            ('adresse', 'Adresse *', 'entry', None),
            ('codePostal', 'Code postal *', 'entry', None),
            ('ville', 'Ville *', 'entry', None),
            ('telephone', 'Téléphone', 'entry', None),
            ('email', 'Email', 'entry', None),
            ('numeroSiret', 'N° SIRET (si entreprise)', 'entry', None),
            ('profession', 'Profession', 'entry', None)
        ]
        
        # Création des champs en grille
        for i, (field, label, field_type, options) in enumerate(client_fields):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            tk.Label(client_frame, text=label, bg='#ffffff', 
                    font=('Segoe UI', 9)).grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            
            # Champ de saisie
            if field_type == 'combobox':
                var = tk.StringVar(value=self.project_data.get('client', {}).get(field, ''))
                combo = ttk.Combobox(client_frame, textvariable=var, values=options, width=20)
                combo.grid(row=row, column=col+1, sticky=tk.EW, padx=5, pady=5)
                self.client_vars[field] = var
            else:
                var = tk.StringVar(value=self.project_data.get('client', {}).get(field, ''))
                entry = tk.Entry(client_frame, textvariable=var, width=25, font=('Segoe UI', 9))
                entry.grid(row=row, column=col+1, sticky=tk.EW, padx=5, pady=5)
                self.client_vars[field] = var
                
                # Validation en temps réel
                var.trace_add('write', lambda *args, f=field: self._on_field_change('client', f))
        
        # Configuration de la grille
        for i in range(2):
            client_frame.columnconfigure(i*2+1, weight=1)
    
    def _create_project_step(self):
        """Crée l'étape des informations projet"""
        project_frame = tk.LabelFrame(self.scrollable_frame, text="Informations Projet", 
                                    bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        project_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.project_vars = {}
        project_fields = [
            ('adresseProjet', 'Adresse du projet *', 'entry'),
            ('codePostalProjet', 'Code postal projet', 'entry'),
            ('villeProjet', 'Ville projet', 'entry'),
            ('referenceCadastrale', 'Référence cadastrale', 'entry'),
            ('surfaceTerrain', 'Surface terrain (m²)', 'number'),
            ('surfacePlancher', 'Surface de plancher (m²)', 'number'),
            ('empriseSol', 'Emprise au sol (m²)', 'number'),
            ('hauteurBatiment', 'Hauteur bâtiment (m)', 'number'),
            ('nombreNiveaux', 'Nombre de niveaux', 'number'),
            ('dateDepotSouhaitee', 'Date de dépôt souhaitée', 'date')
        ]
        
        for i, (field, label, field_type) in enumerate(project_fields):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(project_frame, text=label, bg='#ffffff', 
                    font=('Segoe UI', 9)).grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            
            var = tk.StringVar(value=self.project_data.get('projet', {}).get(field, ''))
            entry = tk.Entry(project_frame, textvariable=var, width=25, font=('Segoe UI', 9))
            entry.grid(row=row, column=col+1, sticky=tk.EW, padx=5, pady=5)
            self.project_vars[field] = var
            
            var.trace_add('write', lambda *args, f=field: self._on_field_change('projet', f))
        
        for i in range(2):
            project_frame.columnconfigure(i*2+1, weight=1)
    
    def _create_technical_step(self):
        """Crée l'étape des informations techniques"""
        tech_frame = tk.LabelFrame(self.scrollable_frame, text="Informations Techniques", 
                                 bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        tech_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.technical_vars = {}
        
        # Checkboxes pour les options techniques
        technical_options = [
            ('zoneProtegee', '🏛️ Zone protégée / ABF'),
            ('demolition', '💥 Démolition prévue'),
            ('etudesSol', '🔬 Études de sol nécessaires'),
            ('maitriseOeuvre', '👷 Mission de maîtrise d\'œuvre'),
            ('sousTraitance', '🤝 Sous-traitance prévue')
        ]
        
        for field, label in technical_options:
            var = tk.BooleanVar(value=self.project_data.get('technique', {}).get(field, False))
            cb = tk.Checkbutton(tech_frame, text=label, variable=var, bg='#ffffff', 
                              font=('Segoe UI', 10))
            cb.pack(anchor=tk.W, padx=10, pady=5)
            self.technical_vars[field] = var
            var.trace_add('write', lambda *args, f=field: self._on_field_change('technique', f))
        
        # Informations architecte (pré-remplies)
        architect_frame = tk.LabelFrame(tech_frame, text="👨‍💼 Informations Architecte", 
                                      bg='#f8f9fa', font=('Segoe UI', 9, 'bold'))
        architect_frame.pack(fill=tk.X, padx=10, pady=10)
        
        architect_info = self.project_data.get('technique', {}).get('architecte', {
            'nom': 'Jean MARTIN',
            'numeroOrdre': '123456',
            'telephone': '01.23.45.67.89',
            'email': 'j.martin@architect.fr'
        })
        
        for key, value in architect_info.items():
            tk.Label(architect_frame, text=f"{key.title()}: {value}", 
                    bg='#f8f9fa', font=('Segoe UI', 9)).pack(anchor=tk.W, padx=5, pady=2)
    
    def _create_mission_step(self):
        """Crée l'étape de définition de la mission"""
        mission_frame = tk.LabelFrame(self.scrollable_frame, text="Définition de la Mission", 
                                    bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        mission_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.mission_var = tk.StringVar(value=self.project_data.get('mission', {}).get('type', 'permis_construire'))
        
        missions = [
            ('permis_construire', '📋 Permis de construire uniquement', 'Dossier PC + suivi instruction'),
            ('complete', '🏗️ Mission complète', 'De l\'esquisse à la réception des travaux'),
            ('maitrise_oeuvre', '👷 Maîtrise d\'œuvre', 'Suivi et direction des travaux'),
            ('expertise', '🔍 Expertise/Conseil', 'Mission de conseil ponctuel')
        ]
        
        for value, label, description in missions:
            frame = tk.Frame(mission_frame, bg='#ffffff')
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            rb = tk.Radiobutton(frame, text=label, variable=self.mission_var, value=value,
                              bg='#ffffff', font=('Segoe UI', 10),
                              command=self._on_mission_change)
            rb.pack(side=tk.LEFT)
            
            desc_label = tk.Label(frame, text=description, bg='#ffffff', 
                                fg='#6c757d', font=('Segoe UI', 9))
            desc_label.pack(side=tk.LEFT, padx=(10,0))
        
        # Zone d'estimation des honoraires
        self.honoraires_frame = tk.LabelFrame(mission_frame, text="💰 Estimation Honoraires", 
                                            bg='#f8f9fa', font=('Segoe UI', 9, 'bold'))
        self.honoraires_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self._update_honoraires_estimation()
    
    def _create_validation_step(self):
        """Crée l'étape de validation finale"""
        # Résumé du projet
        summary_frame = tk.LabelFrame(self.scrollable_frame, text="📋 Résumé du Projet", 
                                    bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        summary_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Génération du résumé automatique
        summary_text = self._generate_project_summary()
        
        summary_label = tk.Label(summary_frame, text=summary_text, bg='#ffffff', 
                               font=('Segoe UI', 9), justify=tk.LEFT, wraplength=500)
        summary_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # Documents à générer
        docs_frame = tk.LabelFrame(self.scrollable_frame, text="📄 Documents à Générer", 
                                 bg='#ffffff', font=('Segoe UI', 10, 'bold'))
        docs_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Analyse et génération des documents recommandés
        try:
            analysis = self._get_full_analysis()
            documents = analysis.get('analyse_reglementaire', {}).get('autorisations_requises', [])
            
            self.doc_vars = {}
            for doc in documents:
                var = tk.BooleanVar(value=doc.get('obligatoire', True))
                frame = tk.Frame(docs_frame, bg='#ffffff')
                frame.pack(fill=tk.X, padx=10, pady=2)
                
                cb = tk.Checkbutton(frame, text=doc.get('type', ''), variable=var, bg='#ffffff')
                cb.pack(side=tk.LEFT)
                
                # Indicateur obligatoire/optionnel
                if doc.get('obligatoire'):
                    tk.Label(frame, text="(Obligatoire)", fg='red', bg='#ffffff', 
                           font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=(5,0))
                else:
                    tk.Label(frame, text="(Optionnel)", fg='orange', bg='#ffffff', 
                           font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=(5,0))
                
                self.doc_vars[doc.get('type', '')] = var
        except Exception as e:
            tk.Label(docs_frame, text=f"Erreur d'analyse: {e}", bg='#ffffff', 
                    fg='red').pack(padx=10, pady=10)
        
        # Boutons d'action finale
        action_frame = tk.Frame(self.scrollable_frame, bg='#f8f9fa')
        action_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Button(action_frame, text="📥 Générer tous les PDF", 
                  command=self._generate_all_pdfs, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="💾 Sauvegarder le projet", 
                  command=self._save_final_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📊 Rapport d'analyse", 
                  command=self._show_analysis_report).pack(side=tk.LEFT, padx=5)
    
    def _setup_auto_completion(self):
        """Configure l'auto-complétion et les suggestions"""
        # Auto-save toutes les 30 secondes
        self.master.after(30000, self._auto_save)
        
        # Mise à jour de l'analyse toutes les 2 secondes
        self.master.after(2000, self._periodic_update)
    
    def _update_analysis(self):
        """Met à jour le panneau d'analyse en temps réel"""
        # Nettoyer le contenu existant
        for widget in self.analysis_content.winfo_children():
            widget.destroy()
        
        try:
            # Analyse complète du projet
            analysis = self._get_full_analysis()
            
            # Taux de completion
            completion_frame = tk.LabelFrame(self.analysis_content, text="📈 Progression", 
                                           bg='#ffffff', font=('Segoe UI', 9, 'bold'))
            completion_frame.pack(fill=tk.X, padx=10, pady=5)
            
            completion = self._calculate_completion()
            tk.Label(completion_frame, text=f"{completion}% complété", 
                    bg='#ffffff', font=('Segoe UI', 12, 'bold'), 
                    fg='#007bff').pack(pady=5)
            
            # Barre de progression
            progress = ttk.Progressbar(completion_frame, length=200, mode='determinate')
            progress['value'] = completion
            progress.pack(pady=5)
            
            # Autorisations requises
            if analysis.get('analyse_reglementaire', {}).get('autorisations_requises'):
                auth_frame = tk.LabelFrame(self.analysis_content, text="📋 Autorisations", 
                                         bg='#ffffff', font=('Segoe UI', 9, 'bold'))
                auth_frame.pack(fill=tk.X, padx=10, pady=5)
                
                for auth in analysis['analyse_reglementaire']['autorisations_requises'][:3]:  # Limite à 3
                    auth_text = f"• {auth.get('type', 'N/A')}"
                    if auth.get('obligatoire'):
                        auth_text += " (Obligatoire)"
                    tk.Label(auth_frame, text=auth_text, bg='#ffffff', 
                           font=('Segoe UI', 8), wraplength=250, justify=tk.LEFT).pack(anchor=tk.W, padx=5, pady=1)
            
            # Alertes
            if analysis.get('analyse_reglementaire', {}).get('alertes_conformite'):
                alert_frame = tk.LabelFrame(self.analysis_content, text="⚠️ Alertes", 
                                          bg='#fff3cd', font=('Segoe UI', 9, 'bold'))
                alert_frame.pack(fill=tk.X, padx=10, pady=5)
                
                for alert in analysis['analyse_reglementaire']['alertes_conformite'][:2]:  # Limite à 2
                    tk.Label(alert_frame, text=f"• {alert.get('message', 'N/A')}", 
                           bg='#fff3cd', font=('Segoe UI', 8), wraplength=250, 
                           justify=tk.LEFT, fg='#856404').pack(anchor=tk.W, padx=5, pady=1)
            
            # Estimation honoraires
            if hasattr(self, 'mission_var'):
                honor_frame = tk.LabelFrame(self.analysis_content, text="💰 Honoraires", 
                                          bg='#ffffff', font=('Segoe UI', 9, 'bold'))
                honor_frame.pack(fill=tk.X, padx=10, pady=5)
                
                estimation = analysis.get('estimation_honoraires', {})
                if estimation:
                    total_ht = estimation.get('honoraires_total_ht', 0)
                    tk.Label(honor_frame, text=f"Estimation: {total_ht:,.0f}€ HT", 
                           bg='#ffffff', font=('Segoe UI', 10, 'bold'), 
                           fg='#28a745').pack(pady=5)
        
        except Exception as e:
            error_frame = tk.LabelFrame(self.analysis_content, text="❌ Erreur", 
                                      bg='#f8d7da', font=('Segoe UI', 9, 'bold'))
            error_frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(error_frame, text=f"Erreur d'analyse:\n{str(e)[:100]}...", 
                   bg='#f8d7da', font=('Segoe UI', 8), wraplength=250).pack(padx=5, pady=5)
    
    def _update_sidebar(self):
        """Met à jour la sidebar"""
        for i, frame in enumerate(self.step_frames):
            # Mise à jour visuelle des étapes
            self._update_step_visual(frame, i)
    
    def _update_step_visual(self, frame, index):
        """Met à jour l'apparence visuelle d'une étape"""
        # Trouver le canvas dans le frame
        for child in frame.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Canvas):
                        # Mettre à jour le cercle
                        grandchild.delete("all")
                        if index == self.current_step:
                            color = '#007bff'
                            text_color = 'white'
                        elif index < self.current_step:
                            color = '#28a745'
                            text_color = 'white'
                        else:
                            color = '#e9ecef'
                            text_color = '#6c757d'
                        
                        grandchild.create_oval(2, 2, 28, 28, fill=color, outline=color)
                        grandchild.create_text(15, 15, text=str(index+1), fill=text_color, 
                                            font=('Segoe UI', 10, 'bold'))
                        break
                break
    
    # Event handlers
    def _on_type_change(self):
        """Gère le changement de type de projet"""
        if not hasattr(self, 'project_data'):
            self.project_data = {'projet': {}}
        self.project_data.setdefault('projet', {})['typeProjet'] = self.type_var.get()
        self._trigger_analysis_update()
    
    def _on_destination_change(self):
        """Gère le changement de destination"""
        self.project_data.setdefault('projet', {})['destination'] = self.destination_var.get()
        self._trigger_analysis_update()
    
    def _on_field_change(self, section, field):
        """Gère les changements de champs"""
        try:
            if section == 'client' and hasattr(self, 'client_vars'):
                value = self.client_vars[field].get()
                self.project_data.setdefault('client', {})[field] = value
            elif section == 'projet' and hasattr(self, 'project_vars'):
                value = self.project_vars[field].get()
                self.project_data.setdefault('projet', {})[field] = value
            elif section == 'technique' and hasattr(self, 'technical_vars'):
                value = self.technical_vars[field].get()
                self.project_data.setdefault('technique', {})[field] = value
            
            self._trigger_analysis_update()
        except Exception as e:
            pass  # Ignorer les erreurs de mise à jour
    
    def _on_mission_change(self):
        """Gère le changement de type de mission"""
        self.project_data.setdefault('mission', {})['type'] = self.mission_var.get()
        self._update_honoraires_estimation()
        self._trigger_analysis_update()
    
    def _trigger_analysis_update(self):
        """Déclenche une mise à jour de l'analyse"""
        if self.auto_analysis:
            self.master.after_idle(self._update_analysis)
            self.master.after_idle(self._update_completion_display)
    
    def _update_completion_display(self):
        """Met à jour l'affichage du taux de completion"""
        completion = self._calculate_completion()
        self.completion_label.config(text=f"{completion}%")
        self.progress_bar['value'] = completion
    
    def _calculate_completion(self) -> int:
        """Calcule le taux de completion du projet"""
        total_fields = 15  # Nombre total de champs importants
        filled_fields = 0
        
        # Champs client essentiels
        client = self.project_data.get('client', {})
        essential_client = ['nom', 'prenom', 'adresse', 'codePostal', 'ville']
        filled_fields += sum(1 for field in essential_client if client.get(field))
        
        # Champs projet essentiels
        projet = self.project_data.get('projet', {})
        essential_projet = ['typeProjet', 'adresseProjet', 'destination', 'surfacePlancher']
        filled_fields += sum(1 for field in essential_projet if projet.get(field))
        
        # Mission définie
        if self.project_data.get('mission', {}).get('type'):
            filled_fields += 1
        
        # Calcul des champs optionnels
        optional_fields = ['telephone', 'email', 'surfaceTerrain', 'referenceCadastrale']
        optional_filled = sum(1 for section in [client, projet] 
                            for field in optional_fields 
                            if section.get(field))
        
        # Pondération: 80% essentiels + 20% optionnels
        essential_rate = (filled_fields / total_fields) * 80
        optional_rate = min(optional_filled / len(optional_fields), 1) * 20
        
        return min(100, int(essential_rate + optional_rate))
    
    def _get_full_analysis(self) -> Dict[str, Any]:
        """Obtient l'analyse complète du projet"""
        try:
            # Convertir les données pour l'analyse
            analysis_data = self._prepare_data_for_analysis()
            # Obtenir l'analyse intelligente
            return self.architect_logic.analyser_projet(analysis_data)
        except Exception as e:
            return {'error': str(e)}
    
    def _prepare_data_for_analysis(self) -> Dict[str, Any]:
        """Prépare les données pour l'analyse"""
        # Conversion des variables Tkinter en valeurs Python
        prepared_data = {
            'client': {},
            'projet': {},
            'technique': {}
        }
        
        # Client data
        if hasattr(self, 'client_vars'):
            for field, var in self.client_vars.items():
                prepared_data['client'][field] = var.get()
        
        # Project data
        if hasattr(self, 'project_vars'):
            for field, var in self.project_vars.items():
                prepared_data['projet'][field] = var.get()
        
        # Technical data
        if hasattr(self, 'technical_vars'):
            for field, var in self.technical_vars.items():
                prepared_data['technique'][field] = var.get()
        
        # Type et destination depuis les variables globales
        if hasattr(self, 'type_var'):
            prepared_data['projet']['typeProjet'] = self.type_var.get()
        if hasattr(self, 'destination_var'):
            prepared_data['projet']['destination'] = self.destination_var.get()
        
        return prepared_data
    
    # Navigation methods
    def _next_step(self):
        """Passe à l'étape suivante"""
        if self.current_step < len(self.steps) - 1:
            # Validation de l'étape actuelle
            if self._validate_current_step():
                self.current_step += 1
                self._update_content()
                self._update_sidebar()
                self._update_navigation_buttons()
    
    def _previous_step(self):
        """Revient à l'étape précédente"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_content()
            self._update_sidebar()
            self._update_navigation_buttons()
    
    def _update_navigation_buttons(self):
        """Met à jour l'état des boutons de navigation"""
        self.prev_button.config(state='normal' if self.current_step > 0 else 'disabled')
        
        if self.current_step == len(self.steps) - 1:
            self.next_button.config(text="Terminer", command=self._finish_wizard)
        else:
            self.next_button.config(text="Suivant →", command=self._next_step)
    
    def _validate_current_step(self) -> bool:
        """Valide l'étape actuelle"""
        if self.current_step == 0:
            # Validation type de projet
            if not hasattr(self, 'type_var') or not self.type_var.get():
                messagebox.showwarning("Validation", "Veuillez sélectionner un type de projet")
                return False
        elif self.current_step == 1:
            # Validation client
            required_fields = ['nom', 'prenom', 'adresse']
            if hasattr(self, 'client_vars'):
                for field in required_fields:
                    if not self.client_vars.get(field, tk.StringVar()).get().strip():
                        messagebox.showwarning("Validation", f"Le champ '{field}' est obligatoire")
                        return False
        return True
    
    def _finish_wizard(self):
        """Termine l'assistant"""
        if self._validate_current_step():
            messagebox.showinfo("Terminé", "Assistant terminé avec succès!\nVous pouvez maintenant générer vos documents.")
    
    # Utility methods
    def _load_template(self, template_name: str):
        """Charge un template de projet"""
        templates = {
            'maison_120': {
                'client': {'nom': 'Martin', 'prenom': 'Pierre', 'adresse': '15 rue de la Paix', 
                          'codePostal': '75001', 'ville': 'Paris'},
                'projet': {'typeProjet': 'construction_neuve', 'destination': 'habitation',
                          'surfacePlancher': '120', 'surfaceTerrain': '500', 
                          'adresseProjet': '10 avenue des Champs, Paris'}
            },
            'extension_30': {
                'client': {'nom': 'Dupont', 'prenom': 'Marie', 'adresse': '25 rue Victor Hugo',
                          'codePostal': '69001', 'ville': 'Lyon'},
                'projet': {'typeProjet': 'extension', 'destination': 'habitation',
                          'surfacePlancher': '30', 'adresseProjet': '25 rue Victor Hugo, Lyon'}
            },
            'renovation': {
                'client': {'nom': 'SARL Bâtiment', 'numeroSiret': '12345678901234',
                          'adresse': '50 rue de l\'Industrie', 'codePostal': '33000', 'ville': 'Bordeaux'},
                'projet': {'typeProjet': 'renovation', 'destination': 'commerce',
                          'adresseProjet': '12 place du Marché, Bordeaux'}
            }
        }
        
        if template_name in templates:
            template = templates[template_name]
            self.project_data.update(template)
            
            # Mise à jour des variables si elles existent
            if hasattr(self, 'type_var') and 'typeProjet' in template.get('projet', {}):
                self.type_var.set(template['projet']['typeProjet'])
            if hasattr(self, 'destination_var') and 'destination' in template.get('projet', {}):
                self.destination_var.set(template['projet']['destination'])
            
            # Mise à jour des champs client
            if hasattr(self, 'client_vars'):
                for field, value in template.get('client', {}).items():
                    if field in self.client_vars:
                        self.client_vars[field].set(value)
            
            # Mise à jour des champs projet  
            if hasattr(self, 'project_vars'):
                for field, value in template.get('projet', {}).items():
                    if field in self.project_vars:
                        self.project_vars[field].set(value)
            
            messagebox.showinfo("Template", f"Template '{template_name}' chargé avec succès!")
            self._trigger_analysis_update()
    
    def _save_project(self):
        """Sauvegarde le projet"""
        try:
            filename = f"projet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = Config.CERFA_DATA_DIR / filename
            
            # Préparer les données pour la sauvegarde
            save_data = self._prepare_data_for_analysis()
            save_data['meta'] = {
                'created': datetime.now().isoformat(),
                'version': '1.0',
                'completion_rate': self._calculate_completion()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Sauvegarde", f"Projet sauvegardé: {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de sauvegarde: {e}")
    
    def _load_project(self):
        """Charge un projet sauvegardé"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                initialdir=Config.CERFA_DATA_DIR,
                title="Charger un projet",
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Mettre à jour les données du projet
                self.project_data.update(loaded_data)
                
                # Recharger l'interface
                self._update_content()
                self._trigger_analysis_update()
                
                messagebox.showinfo("Chargement", "Projet chargé avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de chargement: {e}")
    
    def _update_honoraires_estimation(self):
        """Met à jour l'estimation des honoraires"""
        if hasattr(self, 'honoraires_frame'):
            # Nettoyer les widgets existants
            for widget in self.honoraires_frame.winfo_children():
                widget.destroy()
            
            try:
                analysis = self._get_full_analysis()
                estimation = analysis.get('estimation_honoraires', {})
                
                if estimation:
                    # Affichage des honoraires
                    tk.Label(self.honoraires_frame, text=f"Coût travaux estimé: {estimation.get('cout_travaux_estime', 0):,.0f}€ HT", 
                           bg='#f8f9fa', font=('Segoe UI', 9)).pack(anchor=tk.W, padx=5, pady=2)
                    tk.Label(self.honoraires_frame, text=f"Taux honoraires: {estimation.get('taux_honoraires_base', 0):.1f}%", 
                           bg='#f8f9fa', font=('Segoe UI', 9)).pack(anchor=tk.W, padx=5, pady=2)
                    tk.Label(self.honoraires_frame, text=f"Honoraires HT: {estimation.get('honoraires_total_ht', 0):,.0f}€", 
                           bg='#f8f9fa', font=('Segoe UI', 10, 'bold'), fg='#007bff').pack(anchor=tk.W, padx=5, pady=2)
                    tk.Label(self.honoraires_frame, text=f"Honoraires TTC: {estimation.get('honoraires_ttc', 0):,.0f}€", 
                           bg='#f8f9fa', font=('Segoe UI', 10, 'bold'), fg='#28a745').pack(anchor=tk.W, padx=5, pady=2)
                else:
                    tk.Label(self.honoraires_frame, text="Données insuffisantes pour l'estimation", 
                           bg='#f8f9fa', font=('Segoe UI', 9), fg='#6c757d').pack(padx=5, pady=5)
                    
            except Exception as e:
                tk.Label(self.honoraires_frame, text=f"Erreur calcul: {str(e)[:50]}", 
                       bg='#f8f9fa', font=('Segoe UI', 8), fg='red').pack(padx=5, pady=5)
    
    def _generate_project_summary(self) -> str:
        """Génère un résumé du projet"""
        data = self._prepare_data_for_analysis()
        
        client = data.get('client', {})
        projet = data.get('projet', {})
        
        summary_parts = []
        
        if client.get('nom'):
            summary_parts.append(f"Client: {client.get('civilite', '')} {client.get('nom', '')} {client.get('prenom', '')}")
        
        if projet.get('typeProjet'):
            summary_parts.append(f"Type: {projet.get('typeProjet', '').replace('_', ' ').title()}")
        
        if projet.get('surfacePlancher'):
            summary_parts.append(f"Surface: {projet.get('surfacePlancher')}m²")
        
        if projet.get('adresseProjet'):
            summary_parts.append(f"Lieu: {projet.get('adresseProjet')}")
        
        return "\n".join(summary_parts) if summary_parts else "Projet en cours de définition..."
    
    def _generate_all_pdfs(self):
        """Génère tous les PDF sélectionnés"""
        try:
            if hasattr(self, 'doc_vars'):
                selected_docs = [doc_type for doc_type, var in self.doc_vars.items() if var.get()]
                if selected_docs:
                    project_data = self._prepare_data_for_analysis()
                    for doc_type in selected_docs:
                        # Extraire l'ID du CERFA à partir du type de document (ex: "cerfa_13406-15")
                        match = re.search(r'(\d{5}-\d{2})', doc_type)
                        if not match:
                            print(f"Impossible d'extraire l'ID du CERFA pour: {doc_type}")
                            continue
                        
                        cerfa_id = match.group(1)
                        output_filename = f"cerfa_{cerfa_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        output_path = Config.FILLED_PDFS_DIR / output_filename
                        
                        fill_pdf(cerfa_id, project_data, str(output_path))
                    
                    messagebox.showinfo("Génération", f"{len(selected_docs)} documents générés avec succès dans le dossier 'filled_pdfs'.")
                else:
                    messagebox.showwarning("Sélection", "Aucun document sélectionné")
            else:
                messagebox.showwarning("Données", "Veuillez d'abord compléter l'analyse du projet")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de génération: {e}")
    
    def _save_final_project(self):
        """Sauvegarde finale du projet complet"""
        self._save_project()
    
    def _show_analysis_report(self):
        """Affiche le rapport d'analyse détaillé"""
        try:
            analysis = self._get_full_analysis()
            
            # Créer une nouvelle fenêtre pour le rapport
            report_window = tk.Toplevel(self.master)
            report_window.title("Rapport d'Analyse Détaillé")
            report_window.geometry("800x600")
            
            # Zone de texte scrollable
            text_widget = scrolledtext.ScrolledText(report_window, wrap=tk.WORD, font=('Courier', 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Formatage du rapport
            report_text = self._format_analysis_report(analysis)
            text_widget.insert(tk.END, report_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de génération du rapport: {e}")
    
    def _format_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Formate le rapport d'analyse"""
        report = []
        report.append("="*80)
        report.append("RAPPORT D'ANALYSE ARCHITECTE - PROJET CERFA")
        report.append("="*80)
        report.append(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        
        # Résumé du projet
        report.append("RÉSUMÉ DU PROJET:")
        report.append("-" * 20)
        report.append(self._generate_project_summary())
        report.append("")
        
        # Autorisations requises
        if analysis.get('analyse_reglementaire', {}).get('autorisations_requises'):
            report.append("AUTORISATIONS D'URBANISME REQUISES:")
            report.append("-" * 40)
            for auth in analysis['analyse_reglementaire']['autorisations_requises']:
                status = "OBLIGATOIRE" if auth.get('obligatoire') else "OPTIONNEL"
                report.append(f"• {auth.get('type', 'N/A')} - {status}")
                report.append(f"  {auth.get('nom', '')}")
                if auth.get('delai_instruction'):
                    report.append(f"  Délai d'instruction: {auth.get('delai_instruction')} jours")
                report.append("")
        
        # Alertes
        if analysis.get('analyse_reglementaire', {}).get('alertes_conformite'):
            report.append("ALERTES ET OBLIGATIONS:")
            report.append("-" * 25)
            for alert in analysis['analyse_reglementaire']['alertes_conformite']:
                report.append(f"⚠️  {alert.get('message', 'N/A')}")
            report.append("")
        
        # Estimation honoraires
        if analysis.get('estimation_honoraires'):
            est = analysis['estimation_honoraires']
            report.append("ESTIMATION HONORAIRES:")
            report.append("-" * 22)
            report.append(f"Coût travaux estimé: {est.get('cout_travaux_estime', 0):,.0f}€ HT")
            report.append(f"Taux honoraires: {est.get('taux_honoraires_base', 0):.1f}%")
            report.append(f"Honoraires total HT: {est.get('honoraires_total_ht', 0):,.0f}€")
            report.append(f"Honoraires TTC: {est.get('honoraires_ttc', 0):,.0f}€")
            report.append("")
        
        # Planning
        if analysis.get('planning_mission', {}).get('phases_mission'):
            report.append("PLANNING DE MISSION:")
            report.append("-" * 19)
            for phase in analysis['planning_mission']['phases_mission']:
                report.append(f"• {phase.get('nom_phase', '')}")
                report.append(f"  Du {phase.get('date_debut', '')} au {phase.get('date_fin', '')}")
                report.append(f"  Durée: {phase.get('duree_semaines', 0)} semaines")
                report.append("")
        
        report.append("="*80)
        report.append("Fin du rapport - ArchiBot Assistant")
        report.append("="*80)
        
        return "\n".join(report)
    
    def _auto_save(self):
        """Sauvegarde automatique"""
        try:
            if self._calculate_completion() > 30:  # Seulement si plus de 30% complété
                auto_save_path = Config.CERFA_DATA_DIR / "auto_save.json"
                save_data = self._prepare_data_for_analysis()
                save_data['meta'] = {
                    'auto_saved': datetime.now().isoformat(),
                    'completion_rate': self._calculate_completion()
                }
                
                with open(auto_save_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Ignorer les erreurs d'auto-save
        
        # Programmer la prochaine sauvegarde
        self.master.after(30000, self._auto_save)
    
    def _periodic_update(self):
        """Mise à jour périodique de l'interface"""
        try:
            if self.auto_analysis:
                self._update_analysis()
                self._update_completion_display()
        except Exception:
            pass
        
        # Programmer la prochaine mise à jour
        self.master.after(2000, self._periodic_update)

def main():
    """Fonction principale pour lancer l'interface intelligente"""
    root = tk.Tk()
    app = ProgressiveFormWizard(root)
    
    # Configuration de la fermeture
    def on_closing():
        if messagebox.askokcancel("Quitter", "Voulez-vous sauvegarder avant de quitter?"):
            app._save_project()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()