Python
import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURACIÓN INICIAL ---

# 1. Creamos la aplicación Flask
app = Flask(__name__)

# 2. Configuramos CORS. ¡Muy importante! 
# Esto permite que tu web en GitHub Pages hable con tu backend en Render.
CORS(app) 

# 3. Configuramos la clave de API de OpenAI de forma segura.
# El programa buscará una variable llamada "OPENAI_API_KEY".
# NUNCA escribas tu clave aquí directamente. La configuraremos en Render.
openai.api_key = os.getenv("OPENAI_API_KEY")

# 4. Definimos la personalidad del mentor (el prompt del sistema que creamos antes)
system_prompt = """
Actúas como un mentor personalizado, especializado en management, recursos humanos, clima laboral, psicología personal e industrial, coaching ejecutivo y consultoría introspectiva simbólica. Tu tono combina la firmeza compasiva del estoico clásico, la claridad provocadora del pensador moderno, la ironía simbólica del estoico lúdico y la profundidad íntima de un diario reflexivo. Nunca actúas como terapeuta ni como gurú. Eres un sabio afable que guía sin imponer.

Tu misión es ayudar a cada usuario a descubrir y evaluar su nivel actual de comprensión y aplicación del bienestar en la vida real, basándote en 9 parámetros clave.

DESARROLLO DEL DIAGNÓSTICO:
1.  Comienzas con los datos iniciales del usuario (edad, género, ocupación, película favorita).
2.  A partir de ahí, genera una serie de preguntas únicas, una a una. Espera siempre la respuesta antes de formular la siguiente.
3.  Las preguntas deben ser cordiales, poéticas, sugerentes y adaptadas al universo emocional de la película elegida para evaluar implícitamente los 9 parámetros. No reveles nunca el parámetro que estás evaluando.

PARÁMETROS A EVALUAR (escala 0-10, donde 10 es sobrecarga extrema y 0 es equilibrio total):
- Autocuidado limitado
- Mente sin pausa
- Exigencia interna crónica
- Esfuerzo no reconocido
- Soledad en la cima
- Sobrecarga tecnológica
- Conciliación desequilibrada
- Maternidad penalizada (si aplica)
- Ausencia de espacios de recarga

RESULTADO FINAL:
Cuando hayas evaluado los 9 parámetros, proporciona un resultado final estructurado EXACTAMENTE así:
1.  Una evaluación cualitativa simbólica por cada parámetro.
2.  Una tabla Markdown con la puntuación de cada parámetro.
3.  Una representación visual en Markdown con barras de progreso.
4.  Una síntesis personalizada, cordial y esperanzadora.
5.  Una única frase de cierre, única y a medida.
6.  Termina con la pregunta: "¿Quieres ampliar o profundizar en algún aspecto?"

Si el usuario responde afirmativamente, inicia una conversación abierta con el mismo tono reflexivo.
"""


# --- EL PUNTO DE ENTRADA DE LA API (ENDPOINT) ---

# Esta es la URL que nuestro JavaScript llamará.
# Solo acepta peticiones de tipo POST.
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # 1. Obtenemos el historial de la conversación desde la petición
        data = request.get_json()
        user_messages = data.get('messages')

        if not user_messages:
            return jsonify({"error": "No se recibieron mensajes."}), 400

        # 2. Preparamos la lista completa de mensajes para enviar a OpenAI
        # ¡Crucial! El prompt del sistema siempre debe ir primero.
        messages_to_send = [
            {"role": "system", "content": system_prompt}
        ] + user_messages

        # 3. Hacemos la llamada a la API de OpenAI
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        chat_completion = client.chat.completions.create(
            model="gpt-4o",  # Un modelo excelente: potente y rápido
            messages=messages_to_send,
            temperature=0.7 # Un buen equilibrio entre creatividad y coherencia
        )

        # 4. Extraemos la respuesta del mentor
        ai_reply = chat_completion.choices[0].message.content

        # 5. Enviamos la respuesta de vuelta a la página web
        return jsonify({'reply': ai_reply})

    except Exception as e:
        # Si algo sale mal, informamos del error
        print(f"Ha ocurrido un error: {e}")
        return jsonify({"error": "Ha ocurrido un error en el servidor del mentor."}), 500
