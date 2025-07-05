CERFA_FIELD_MAPPINGS = {
    "13406-15": { # Permis de construire maison individuelle (PCMI) / Déclaration Préalable
        # --- Demandeur (Client) ---
        "client.civilite": {
            "M.": "D1M_monsieur",
            "Mme": "D1F_madame"
        },
        "client.nom": "D1N_nom",
        "client.prenom": "D1P_prenom",
        "client.dateNaissance": "D1A_naissance",
        "client.lieuNaissance": "D1C_commune",
        "client.adresse": "D3V_voie",
        "client.codePostal": "D3C_code",
        "client.ville": "D3L_localite",
        "client.telephone": "D3T_telephone",
        "client.email": "D5GE1_email",
        "client.numeroSiret": "D2S_siret",

        # --- Terrain ---
        "projet.adresseProjet": "T2V_voie",
        "projet.codePostalProjet": "T2C_code",
        "projet.villeProjet": "T2L_localite",
        "projet.referenceCadastrale": "T2S_section",
        "projet.surfaceTerrain": "T2T_superficie",

        # --- Projet ---
        "projet.typeProjet": {
            "construction_neuve": "C2ZA1_neuve",
            "extension": "C2ZA2_extension",
            "renovation": "C2ZA3_amenagement", # Simplification, rénovation peut être aménagement
        },
        "projet.destination": {
            "habitation": "C2ZR1_destination",
            "commerce": "C2ZR2_destination",
            "industrie": "C2ZR3_destination",
            "erp": "C2ZR4_destination",
            "bureau": "C2ZR5_destination",
            "entrepot": "C2ZR6_destination",
        },
        "projet.surfacePlancher": "C5ZK1_extension", # Surface créée
        "projet.empriseSol": "C5ZJ1_emprise", # Emprise au sol créée
        "projet.hauteurBatiment": None,
        "projet.nombreNiveaux": "C5ZB2_niveaux",
        
        # --- Technique / Architecte ---
        "technique.zoneProtegee": "X1A_ABF",
        "technique.demolition": "C2ZC2_demolir",
        # Les infos architecte sont gérées par ARCHITECT_INTERNAL_MAP
    },
    "14880-02": { # Permis de conduire - Avis Médical
        "client.nom": "topmostSubform[0].Page1[0].txt_nom[0]",
        "client.prenom": "topmostSubform[0].Page1[0].txt_prenom[0]",
        "client.dateNaissance.jour": "topmostSubform[0].Page1[0].txt_jour[0]",
        "client.dateNaissance.mois": "topmostSubform[0].Page1[0].txt_mois[0]",
        "client.dateNaissance.annee": "topmostSubform[0].Page1[0].txt_annee[0]",
        "client.lieuNaissance": "topmostSubform[0].Page1[0].txt_communenaiss[0]",
        "client.adresse": "topmostSubform[0].Page1[0].txt_adresseNom[0]",
        "client.codePostal": "topmostSubform[0].Page1[0].txt_cp[0]",
        "client.ville": "topmostSubform[0].Page1[0].txt_commune[0]",
        "client.telephone": "topmostSubform[0].Page1[0].txt_num[0]",
        "client.email": "topmostSubform[0].Page1[0].txt_courriel[0]",
        "client.civilite": {
            "M.": "topmostSubform[0].Page1[0].btn_sexe[0]", # Assumant que "M." correspond à la première option
            "Mme": "topmostSubform[0].Page1[0].btn_sexe[1]" # Assumant que "Mme" correspond à la seconde
        },
        "client.profession": None,
        "client.numeroSiret": None,
    },
    "13405-13": { # Permis de démolir
        "client.nom": "D1N_nom",
        "client.prenom": "D1P_prenom",
        "client.dateNaissance": "D1A_naissance",
        "client.lieuNaissance": "D1C_commune",
        "client.adresse": "D3V_voie",
        "client.codePostal": "D3C_code",
        "client.ville": "D3L_localite",
        "client.telephone": "D3T_telephone",
        "client.email": "D5GE1_email",
        "client.numeroSiret": "D2S_siret",

        "projet.adresseProjet": "T2V_voie",
        "projet.codePostalProjet": "T2C_code",
        "projet.villeProjet": "T2L_localite",
        "projet.referenceCadastrale": "T2S_section",
        "projet.surfaceTerrain": "T2T_superficie",
        "technique.demolition": "K1J_travaux", # Champ texte, pas une checkbox directe
        "technique.zoneProtegee": "X1A_ABF",
    },
    "13407-10": { # Déclaration d'ouverture de chantier
        "client.nom": "D1N_nom",
        "client.prenom": "D1P_prenom",
        "client.adresse": "D3V_voie",
        "client.codePostal": "D3C_code",
        "client.ville": "D3L_localite",
        "client.email": "D5GE1_email",
        "client.numeroSiret": "D2S_siret",

        "projet.adresseProjet": "D3V_voie", # L'adresse du projet est souvent l'adresse du demandeur sur ce formulaire
        "projet.codePostalProjet": "D3C_code",
        "projet.villeProjet": "D3L_localite",
        "projet.dateDepotSouhaitee": "C9B_ouverture", # Date d'ouverture de chantier
    },
    "13410-12": { # Demande de certificat d'urbanisme
        "client.nom": "D1N_nom",
        "client.prenom": "D1P_prenom",
        "client.adresse": "D3V_voie",
        "client.codePostal": "D3C_code",
        "client.ville": "D3L_localite",
        "client.telephone": "D3T_telephone",
        "client.email": "D5GE1_email",
        "client.numeroSiret": "D2S_siret",

        "projet.adresseProjet": "T2V_voie",
        "projet.codePostalProjet": "T2C_code",
        "projet.villeProjet": "T2L_localite",
        "projet.referenceCadastrale": "T2S_section",
        "projet.surfaceTerrain": "T2T_superficie",
        "projet.typeProjet": "C2UD4_nature", # Nature du projet
        "projet.destination": "C2ZD1_description", # Description du projet
    },
    "13824-04": { # Demande d'autorisation ERP
        "client.nom": "Nom",
        "client.prenom": "Prnom",
        "client.dateNaissance": "Date de naissance",
        "client.adresse": "Adresse Numro",
        "client.codePostal": "CP",
        "client.ville": "Localit",
        "client.telephone": "Tlphone portable_2",
        "client.email": "courriel_1",
        "client.profession": "Activit principale exerce dans ltablissement par tages 1",
        "client.numeroSiret": "Siret",

        "projet.adresseProjet": "Adresse Numro",
        "projet.codePostalProjet": "CP",
        "projet.villeProjet": "Localit",
        "projet.surfacePlancher": "Surface de plancher aprs travaux",
        "projet.typeProjet": "Construction neuve", # Ceci est un champ texte, pas une checkbox
        "projet.destination": "Types de locaux local  taux doccupation1er tage",

        "technique.demolition": "Travaux damnagement remplacement de revtements rnovation lectrique cration dune rampe par exemple",
        "technique.zoneProtegee": "X1A_ABF",
    },
    "16702-01": { # Déclaration préalable de travaux, constructions et aménagements
        "client.nom": "D1N_nom",
        "client.prenom": "D1P_prenom",
        "client.dateNaissance": "D1A_naissance",
        "client.lieuNaissance": "D1C_commune",
        "client.adresse": "D3V_voie",
        "client.codePostal": "D3C_code",
        "client.ville": "D3L_localite",
        "client.telephone": "D3T_telephone",
        "client.email": "D5GE1_email",
        "client.numeroSiret": "D2S_siret",

        "projet.adresseProjet": "T2V_voie",
        "projet.codePostalProjet": "T2C_code",
        "projet.villeProjet": "T2L_localite",
        "projet.referenceCadastrale": "T2S_section",
        "projet.surfaceTerrain": "T2T_superficie",
        "projet.surfacePlancher": "C5ZK1_extension",
        "projet.typeProjet": "C2ZR1_destination",
        "projet.destination": "C2ZR1_destination",

        "technique.demolition": "C2ZC3_cloture",
        "technique.zoneProtegee": "X1A_ABF",
    },
    "13408-12": { # Déclaration attestant l'achèvement et la conformité des travaux (DAACT)
        "client.nom": "D1N_nom",
        "client.prenom": "D1P_prenom",
        "client.adresse": "D3V_voie",
        "client.codePostal": "D3C_code",
        "client.ville": "D3L_localite",
        "client.email": "D5GE1_email",
        "client.numeroSiret": "D2S_siret",

        "projet.adresseProjet": "D3V_voie", # L'adresse du projet est souvent l'adresse du demandeur sur ce formulaire
        "projet.codePostalProjet": "D3C_code",
        "projet.villeProjet": "D3L_localite",
        "projet.dateDepotSouhaitee": "C9A_acheve", # Date d'achèvement des travaux

        "technique.architecte.nom": "E4S_signaturearchi", # Nom de l'architecte pour la signature
        "technique.architecte.adresse": "E4G_lieuarchi", # Lieu de signature (ville de l'architecte)
        "technique.date_signature": "E4D_datearcchi", # Date de signature de l'architecte
    },
}
