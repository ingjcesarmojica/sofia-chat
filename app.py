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
            # Devolver tanto el contenido base64 como la URL de datos
            return jsonify({
                'audioContent': audio_content,
                'audioUrl': f"data:audio/mp3;base64,{audio_content}"
            })
        else:
            return jsonify({'error': f'API error: {response.status_code}', 'details': response.text}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para procesar mensajes del chat"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Respuestas predefinidas basadas en palabras clave
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hola', 'buenos días', 'buenas tardes', 'saludos']):
            response = "¡Hola! Soy Sofia, tu representante de atención al cliente. ¿En qué puedo ayudarte hoy?"
        elif any(word in message_lower for word in ['abogado', 'legal', 'ley', 'juicio', 'demanda']):
            response = "Entiendo que necesitas asesoría legal. Puedo ayudarte a conectar con nuestros abogados especializados. ¿Podrías contarme más detalles sobre tu situación?"
        elif any(word in message_lower for word in ['precio', 'costo', 'tarifa', 'honorarios']):
            response = "Los honorarios varían según la complejidad del caso. Ofrecemos una consulta inicial gratuita para evaluar tu situación y proporcionarte un presupuesto transparente."
        elif any(word in message_lower for word in ['contacto', 'teléfono', 'email', 'dirección']):
            response = "Puedes contactarnos al teléfono +34 912 345 678, por email a info@fusaabogados.com o visitarnos en Calle Principal 123, Madrid. ¿Te gustaría agendar una cita?"
        elif any(word in message_lower for word in ['gracias', 'agradecer', 'amable']):
            response = "¡Es un placer ayudarte! Estoy aquí para lo que necesites. ¿Hay algo más en lo que pueda asistirte?"
        else:
            # Respuesta por defecto
            responses = [
                "Entiendo tu consulta. Déjame verificar esa información para ti.",
                "Gracias por tu mensaje. Estoy buscando la mejor solución para tu caso.",
                "Comprendo tu situación. Permíteme ayudarte con eso.",
                "Excelente pregunta. Déjame consultar los detalles para darte una respuesta precisa.",
                "Tomo nota de tu consulta. Estoy procesando la información para brindarte la mejor asistencia."
            ]
            response = responses[len(message) % len(responses)]
        
        return jsonify({'response': response})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
