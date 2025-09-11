import os
import requests
import base64
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# Cargar variables del entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración desde variables de entorno
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_API_KEY")
AUDIO_FOLDER = os.getenv("AUDIO_FOLDER", "audio")
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es-ES")
VOICE_NAME = os.getenv("VOICE_NAME", "es-ES-Standard-A")

# Crear carpeta de audio
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Servir la página principal"""
    return render_template('index.html')

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Endpoint para generar audio usando Google TTS"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not GOOGLE_TTS_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500
        
        # Llamar a la API de Google TTS
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_API_KEY}"
        
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": LANGUAGE_CODE,
                "name": VOICE_NAME
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 1.0,
                "pitch": 0.0
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            audio_content = response.json()["audioContent"]
            return jsonify({'audioContent': audio_content})
        else:
            return jsonify({'error': f'API error: {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_message():
    """Endpoint para manejar mensajes del chat"""
    try:
        data = request.json
        message = data.get('message', '')
        
        # Aquí puedes integrar con tu lógica de chatbot o IA
        responses = [
            "Entiendo tu consulta. Déjame verificar esa información para ti.",
            "Gracias por tu mensaje. Estoy buscando la mejor solución para tu caso.",
            "Comprendo tu situación. Permíteme ayudarte con eso.",
            "Excelente pregunta. Déjame consultar los detalles para darte una respuesta precisa."
        ]
        
        response = {
            'text': responses[len(message) % len(responses)],  # Respuesta simple
            'shouldSpeak': True
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
