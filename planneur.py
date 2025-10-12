# 
# 
#   A la date du 13/10/2025, CET ALGO EST LA VERSION LA PLUS ABOUTIE, ET FONCTIONNELLE.
#   C'est sur ce code qu'il faut travailler !!
#
#

import json
from collections import defaultdict

# Exemple de données pour les morceaux
morceaux = [
    {"titre": "Dream Girl", "musiciens": ["Ugo", "Stan", "Titou", "Lisa"]},
    {"titre": "Get Lucky", "musiciens": ["Ugo", "Titou"]}
]

# Exemple de disponibilités sous forme de listes de plages horaires par jour
# Format : [Lundi, Mardi, Mercredi, Jeudi, Vendredi]
# Chaque jour est une liste de plages [heure_debut, heure_fin]
#--------------------------------------------------------------

#Règle simple :
#   [] = aucune disponibilité ce jour-là
#   [[10, 12], [14, 16]] = disponible de 10h à 12h ET de 14h à 16h
disponibilites = {
    "Ugo": [
        [],  # Lundi
        [[10, 12]],  # Mardi
        [[14, 18]],  # Mercredi
        [[14.5, 16]],  # Jeudi
        []   # Vendredi
    ],
    "Stan": [
        [],  # Lundi
        [],  # Mardi
        [],  # Mercredi
        [[15.5, 16]],  # Jeudi
        []   # Vendredi
    ],
    "Titou": [
        [],  # Lundi
        [[10, 12]],  # Mardi
        [[15, 17]],  # Mercredi
        [[14, 19]],  # Jeudi
        []   # Vendredi
    ],
     "Lisa": [
        [],  # Lundi
        [[10, 12]],  # Mardi
        [],  # Mercredi
        [[14, 19]],  # Jeudi
        []   # Vendredi
    ]
}

# Noms des jours pour l'affichage
jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

# Fonction pour découper une plage horaire en créneaux de 30 minutes
def decouper_plage_en_creneaux(debut, fin):
    creneaux = []
    heure_courante = debut
    while heure_courante + 0.5 <= fin:
        creneaux.append((heure_courante, heure_courante + 0.5))
        heure_courante += 0.5
    return creneaux

def obtenir_creneaux_musicien(disponibilites_musicien):
    tous_creneaux = []
    for jour_idx, plages in enumerate(disponibilites_musicien):
        for plage in plages:
            if len(plage) == 2:
                debut, fin = plage
                creneaux = decouper_plage_en_creneaux(debut, fin)
                for creneau in creneaux:
                    # S'assurer que c'est bien un tuple
                    tous_creneaux.append((jour_idx, tuple(creneau) if isinstance(creneau, list) else creneau))
    return tous_creneaux

# Fonction pour trouver les créneaux communs de 30 minutes entre plusieurs musiciens
def trouver_creneaux_communs(musiciens, disponibilites):
    creneaux_par_musicien = []
    for musicien in musiciens:
        if musicien in disponibilites:
            creneaux = obtenir_creneaux_musicien(disponibilites[musicien])
            creneaux_par_musicien.append(set(creneaux))
        else:
            print(f"Attention : le musicien {musicien} n'a pas de disponibilités enregistrées.")
            return []  # ← Déjà correct

    # Trouver l'intersection des créneaux entre tous les musiciens
    if not creneaux_par_musicien:
        return []  # ← Déjà correct

    creneaux_communs = set(creneaux_par_musicien[0])
    for creneaux in creneaux_par_musicien[1:]:
        creneaux_communs.intersection_update(creneaux)

    return list(creneaux_communs)

# Fonction pour générer le planning
def generer_planning(morceaux, disponibilites):
    planning = defaultdict(list)
    morceaux_restants = morceaux.copy()
    creneaux_occupes = set()
    tentatives_max = len(morceaux) * 10  # Limite de sécurité
    tentatives = 0

    while morceaux_restants and tentatives < tentatives_max:
        morceau = morceaux_restants.pop(0)
        musiciens = morceau["musiciens"]
        creneaux_communs = trouver_creneaux_communs(musiciens, disponibilites)

        # Trouver un créneau non occupé
        creneau_trouve = None
        for jour_idx, (debut, fin) in creneaux_communs:
            creneau_str = f"{jours_semaine[jour_idx]} {int(debut)}h{int((debut % 1) * 60):02d}-{int(fin)}h{int((fin % 1) * 60):02d}"
            if creneau_str not in creneaux_occupes:
                creneau_trouve = (jour_idx, (debut, fin))
                break

        if creneau_trouve:
            jour_idx, (debut, fin) = creneau_trouve
            creneau_str = f"{jours_semaine[jour_idx]} {int(debut)}h{int((debut % 1) * 60):02d}-{int(fin)}h{int((fin % 1) * 60):02d}"
            planning[creneau_str].append(morceau["titre"])
            creneaux_occupes.add(creneau_str)
            tentatives = 0  # Réinitialiser le compteur après un succès
        else:
            morceaux_restants.append(morceau)
            tentatives += 1
            if tentatives >= len(morceaux_restants) * 5:
                print(f"⚠️  Impossible de planifier : {morceau['titre']} (musiciens: {', '.join(musiciens)})")
                break

    return planning

# Générer le planning
planning = generer_planning(morceaux, disponibilites)

# Convertir le planning en JSON
planning_json = json.dumps(planning, indent=4, ensure_ascii=False)

print(planning_json)
