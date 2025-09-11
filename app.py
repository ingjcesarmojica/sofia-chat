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
            VoiceId='Mia'      # Femenina - Español mexicano  
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
            response = "¡Hola! Un gusto saludarte. Somos la Fundación VANALI. Nuestro objetivo social es apoyar el emprendimiento de las mujeres cabeza de familia a través de cursos de manualidades."
        elif any(word in message_lower for word in ['curso', 'cursos', 'ofrecen', 'qué hacen', 'muñeco', 'noel']):
            response = "Actualmente estamos dictando dos cursos muy especiales y navideños:\n1. Curso de Muñeco Papá Noel.\n2. Curso de Muñeco Mamá Noel."
        elif any(word in message_lower for word in ['dónde', 'ubicación', 'lugar', 'dirección', 'fusagasugá']):
            response = "Los cursos son presenciales en la ciudad de Fusagasugá. Las clases se dictan en el Conjunto Andalucía, ubicado en el barrio Gaitán, específicamente frente al Colegio Manuel Humberto. ¡Es muy fácil de encontrar!"
        elif any(word in message_lower for word in ['profesor', 'profesora', 'quién enseña', 'imparte', 'rocío']):
            response = "Nuestros cursos son impartidos por la profesora Rocío, una experta en creación de muñecos y manualidades con más de 20 años de experiencia. ¡Aprenderás muchísimo con ella!"
        elif any(word in message_lower for word in ['inscribir', 'inscripción', 'requisitos', 'cómo me inscribo']):
            response = "Lo primero es realizar tu inscripción a través de nuestros canales de servicio oficiales. Con gusto te puedo proporcionar los contactos para que completes tu proceso."
        elif any(word in message_lower for word in ['materiales', 'incluidos', 'comprar', 'llevar']):
            response = "Para que te centres solo en aprender, el valor del curso incluye todos los materiales necesarios para elaborar tus muñecos. Sin embargo, si lo prefieres, también puedes adquirirlos por tu cuenta."
        elif any(word in message_lower for word in ['dura', 'duración', 'horas', 'clases', 'semanas']):
            response = "La duración es la siguiente:\n- Curso de Papá Noel: 4 clases de 2 horas cada una.\n- Curso de Mamá Noel: 5 clases de 2 horas cada una.\nAmbos se pueden tomar los días martes y jueves."
        elif any(word in message_lower for word in ['horario', 'horarios', 'cuándo', 'días', 'tarde', 'mañana']):
            response = "Tenemos dos horarios disponibles para tu comodidad:\n1. Horario de la mañana: de 9:00 a. m. a 11:00 a. m., de lunes a viernes.\n2. Horario de la tarde: de 3:00 p. m. a 5:00 p. m., de lunes a viernes."
        elif any(word in message_lower for word in ['certificado', 'premio', 'recibo', 'finalizar', 'ganador']):
            response = "¡Por supuesto! Al finalizar, recibirás un certificado que acredita el curso recibido. Además, ¡hay un premio especial si tu muñeco es calificado como el ganador del curso!"
        elif any(word in message_lower for word in ['precio', 'costo', 'valor', 'cuánto cuesta', 'tarifa']):
            response = "Los precios, que incluyen los materiales, son los siguientes:\n\nPara Papá Noel:\n- Tamaño grande (1 metro con 20 cm): $110.000 pesos.\n- Tamaño mediano (60 cm): $90.000 pesos.\n\nPara Mamá Noel:\n- Tamaño grande (1 metro con 20 cm): $120.000 pesos.\n- Tamaño mediano (60 cm): $100.000 pesos."
        elif any(word in message_lower for word in ['gracias', 'agradecer', 'amable', 'thanks']):
            response = "¡Es un placer ayudarte! Estoy aquí para lo que necesites. ¿Hay algo más en lo que pueda asistirte?"
        else:
            responses = [
                "Entiendo tu consulta sobre nuestros cursos. Déjame verificar esa información para ti.",
                "Gracias por tu mensaje. Estoy buscando la mejor información sobre nuestros cursos para ayudarte.",
                "Comprendo tu pregunta sobre la Fundación VANALI. Permíteme ayudarte con eso.",
                "Excelente pregunta sobre nuestros cursos. Déjame consultar los detalles para darte una respuesta precisa.",
                "Tomo nota de tu consulta. Estoy procesando la información para brindarte la mejor asistencia sobre nuestros cursos."
            ]
            response = responses[len(message) % len(responses)]
        
        # Determinar si la respuesta requiere mostrar materiales o formulario
        show_materials = any(word in message_lower for word in ['materiales', 'material', 'fotos', 'imágenes', 'imagenes'])
        show_form = any(word in message_lower for word in ['inscribir', 'inscripción', 'registro', 'registrarse', 'matricular', 'formulario'])
        
        return jsonify({
            'response': response,
            'show_materials': show_materials,
            'show_form': show_form
        })
            
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
