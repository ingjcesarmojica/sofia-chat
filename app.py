import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración desde variables de entorno (compatible con Render)
GOOGLE_TTS_API_KEY = os.environ.get("GOOGLE_API_KEY")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "es-ES")
VOICE_NAME = os.environ.get("VOICE_NAME", "es-ES-Standard-A")

# En Render, no podemos escribir en sistema de archivos como en desarrollo
# Así que eliminamos la creación de carpeta de audio
# y manejamos el audio directamente en memoria

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

# El resto del código se mantiene igual...
