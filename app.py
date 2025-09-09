from flask import Flask, render_template, request, jsonify
import random
import os

app = Flask(__name__)

# Respuestas predefinidas de Sofia
responses = [
    "Hola, ¿en qué puedo ayudarte hoy?",
    "Entiendo tu inquietud, déjame ayudarte con eso.",
    "Claro, puedo resolver eso para ti.",
    "Gracias por contactarnos. ¿Podrías darme más detalles?",
    "Estoy aquí para asistirte con cualquier problema que tengas.",
    "Lamento escuchar eso, permíteme encontrar una solución.",
    "Excelente pregunta, la respuesta es...",
    "Puedo ver que necesitas ayuda con eso, te guiaré paso a paso."
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    response = random.choice(responses)
    return jsonify({'sofia': response})

# Elimina el if __name__ completamente
# No uses app.run()
