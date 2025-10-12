from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/planifier', methods=['POST'])
def planifier():
    data = request.json
    morceaux = data["morceaux"]
    disponibilites = data["disponibilites"]

    # Ici, tu appelles la logique de ton planning_maker.py
    # (copie-colle les fonctions nécessaires)
    planning, morceaux_non_planifies = generer_planning(morceaux, disponibilites)

    return jsonify({
        "planning": planning,
        "morceaux_non_planifies": morceaux_non_planifies
    })

def generer_planning(morceaux, disponibilites):
    # Copie-colle ici les fonctions de planning_maker.py
    # (decouper_plage_en_creneaux, obtenir_creneaux_musicien, etc.)
    # Retourne planning et morceaux_non_planifies
    pass

if __name__ == '__main__':
    app.run(debug=True)
