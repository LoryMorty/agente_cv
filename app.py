from flask import Flask, render_template, request, jsonify
from main import TalentAgentSystem
import os

app = Flask(__name__)
if not os.path.exists('uploads'): os.makedirs('uploads')
agente = TalentAgentSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    path = os.path.join('uploads', file.filename)
    file.save(path)
    risultato = agente.agente_parser(path)
    return f"<html><body><h3>{risultato}</h3><a href='/'>Torna alla Dashboard</a></body></html>"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    risposta = agente.esegui_ricerca(data.get('query'))
    # Convertiamo la risposta in stringa per sicurezza
    return jsonify({"response": str(risposta)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
