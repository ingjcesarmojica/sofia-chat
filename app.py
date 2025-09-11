import os
import requests
import base64
import boto3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configuración AWS Polly
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/speak', methods=['POST'])
def speak_text():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
            app.logger.error("AWS credentials not configured")
            return jsonify({'error': 'AWS credentials not configured'}), 500
        
        # Configurar cliente de Polly
        polly = boto3.client('polly',
                            aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY,
                            region_name=AWS_REGION)
        
        # Sintetizar voz con Polly
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Lucia'  # Voz femenina en español
            # Otras voces en español: 'Enrique', 'Mia', 'Penelope'
        )
        
        # Convertir audio a base64
        audio_data = response['AudioStream'].read()
        audio_content = base64.b64encode(audio_data).decode('utf-8')
        
        return jsonify({
            'audioContent': audio_content,
            'audioUrl': f"data:audio/mp3;base64,{audio_content}"
        })
            
    except (BotoCoreError, ClientError) as error:
        app.logger.error(f"AWS Polly error: {error}")
        return jsonify({'error': f'AWS Polly error: {error}'}), 500
    except Exception as e:
        app.logger.error(f"Exception in speak_text: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Respuestas inteligentes basadas en palabras clave
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hola', 'buenos días', 'buenas tardes', 'saludos']):
            response = "¡Hola! Soy Sofia, tu representante de atención al cliente. ¿En qué puedo ayudarte hoy?"
        elif any(word in message_lower for word in ['abogado', 'legal', 'ley', 'juicio', 'demanda', 'abogados']):
            response = "Entiendo que necesitas asesoría legal. Puedo ayudarte a conectar con nuestros abogados especializados. ¿Podrías contarme más detalles sobre tu situación?"
        elif any(word in message_lower for word in ['precio', 'costo', 'tarifa', 'honorarios', 'cuánto cuesta']):
            response = "Los honorarios varían según la complejidad del caso. Ofrecemos una consulta inicial gratuita para evaluar tu situación y proporcionarte un presupuesto transparente."
        elif any(word in message_lower for word in ['contacto', 'teléfono', 'email', 'dirección', 'ubicación']):
            response = "Puedes contactarnos al teléfono +34 912 345 678, por email a info@fusaabogados.com o visitarnos en Calle Principal 123, Madrid. ¿Te gustaría agendar una cita?"
        elif any(word in message_lower for word in ['gracias', 'agradecer', 'amable', 'thanks']):
            response = "¡Es un placer ayudarte! Estoy aquí para lo que necesites. ¿Hay algo más en lo que pueda asistirte?"
        elif any(word in message_lower for word in ['horario', 'hora', 'días', 'atención']):
            response = "Nuestro horario de atención es de lunes a viernes de 9:00 a 18:00 horas. ¿En qué horario prefieres que te contactemos?"
        else:
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
        app.logger.error(f"Exception in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar el estado del servicio"""
    return jsonify({
        'status': 'healthy',
        'aws_configured': bool(AWS_ACCESS_KEY and AWS_SECRET_KEY),
        'service': 'Amazon Polly'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
