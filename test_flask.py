from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    print("Serveur de test démarré sur http://127.0.0.1:8080")
    app.run(port=8080)