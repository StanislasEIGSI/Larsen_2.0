from flask import Flask, request, jsonify, send_from_directory,session
from collections import defaultdict
import os

app = Flask(__name__)

# Configuration CORS manuelle
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Servir le fichier HTML
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Endpoint de test
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "ok", "message": "Serveur Larsen opérationnel !"})

# Endpoint principal pour générer le planning
@app.route('/planifier', methods=['POST', 'OPTIONS'])
def planifier():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.json
        print("\n📥 Données reçues :")

        print(f"- Morceaux: {len(data.get('morceaux', []))}")
        print(f"- Musiciens: {list(data.get('disponibilites', {}).keys())}")
        
        morceaux = data["morceaux"]
        disponibilites = data["disponibilites"]

        planning, morceaux_non_planifies = generer_planning(morceaux, disponibilites)
        
        print(f"\n✅ Planning généré: {len(planning)} créneaux")
        print(f"⚠️  Non planifiés: {len(morceaux_non_planifies)}")

        return jsonify({
            "planning": planning,
            "morceaux_non_planifies": morceaux_non_planifies
        })
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ========== LOGIQUE DE PLANIFICATION ==========

jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

def decouper_plage_en_creneaux(debut, fin):
    """Découpe une plage horaire en créneaux de 30 minutes"""
    creneaux = []
    heure_courante = debut
    while heure_courante + 0.5 <= fin:
        creneaux.append((heure_courante, heure_courante + 0.5))
        heure_courante += 0.5
    return creneaux

def obtenir_creneaux_musicien(disponibilites_musicien):
    """Récupère tous les créneaux de 30min d'un musicien"""
    tous_creneaux = []
    for jour_idx, plages in enumerate(disponibilites_musicien):
        for plage in plages:
            if len(plage) == 2:
                debut, fin = plage
                creneaux = decouper_plage_en_creneaux(debut, fin)
                for creneau in creneaux:
                    tous_creneaux.append((jour_idx, tuple(creneau) if isinstance(creneau, list) else creneau))
    return tous_creneaux

def trouver_creneaux_communs(musiciens, disponibilites):
    """Trouve les créneaux communs entre plusieurs musiciens"""
    creneaux_par_musicien = []
    for musicien in musiciens:
        if musicien in disponibilites:
            creneaux = obtenir_creneaux_musicien(disponibilites[musicien])
            creneaux_par_musicien.append(set(creneaux))
        else:
            print(f"⚠️  {musicien} n'a pas de disponibilités")
            return []

    if not creneaux_par_musicien:
        return []

    creneaux_communs = set(creneaux_par_musicien[0])
    for creneaux in creneaux_par_musicien[1:]:
        creneaux_communs.intersection_update(creneaux)

    return list(creneaux_communs)

def generer_planning(morceaux, disponibilites):
    """Génère le planning des répétitions"""
    planning = defaultdict(list)
    morceaux_restants = morceaux.copy()
    morceaux_non_planifies = []
    creneaux_occupes = set()
    tentatives_max = len(morceaux) * 10
    tentatives = 0

    while morceaux_restants and tentatives < tentatives_max:
        morceau = morceaux_restants.pop(0)
        musiciens = morceau["musiciens"]
        creneaux_communs = trouver_creneaux_communs(musiciens, disponibilites)

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
            tentatives = 0
        else:
            morceaux_restants.append(morceau)
            tentatives += 1
            if tentatives >= len(morceaux_restants) * 5:
                print(f"❌ Impossible: {morceau['titre']}")
                morceaux_non_planifies.append(morceau["titre"])
                break

    return dict(planning), morceaux_non_planifies

# ========== DÉMARRAGE ==========

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎸 LARSEN 2.0 - Planificateur de répétitions")
    print("=" * 60)
    print(f"📍 Serveur démarré sur: http://127.0.0.1:8080")
    print(f"📍 Interface web: http://127.0.0.1:8080")
    print(f"📍 Test API: http://127.0.0.1:8080/test")
    print("=" * 60)
    print("💡 Appuyez sur Ctrl+C pour arrêter\n")
    
    app.run(debug=True, port=8080, host='127.0.0.1')