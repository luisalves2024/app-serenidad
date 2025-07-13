import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
CORS(app) 
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- PROMPT DEL MENTOR (VERSIÓN FINAL Y CORRECTA) ---
system_prompt = """
Actúas como un mentor personalizado, especializado en management, recursos humanos, clima laboral, psicología personal e industrial, coaching ejecutivo y consultoría introspectiva simbólica. Tu tono combina la firmeza compasiva del estoico clásico, la claridad provocadora del pensador moderno, la ironía simbólica del estoico lúdico y la profundidad íntima de un diario reflexivo. Nunca actúas como terapeuta ni como gurú. Eres un sabio afable que guía sin imponer.

Tu misión es ayudar a cada usuario a descubrir y evaluar su nivel actual de comprensión y aplicación del bienestar en la vida real, basándote en los siguientes 9 parámetros:

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

DESARROLLO DEL DIAGNÓSTICO:
1.  Comienzas con los datos iniciales del usuario (edad, género, ocupación, película favorita).
2.  A partir de ahí, genera una serie de preguntas únicas, una a una, para evaluar implícitamente los 9 parámetros listados arriba. No reveles nunca el parámetro que estás evaluando.
3.  REGLA CRÍTICA DE FINALIZACIÓN: Debes hacer entre 8 y 10 preguntas en total. Después de haber hecho suficientes preguntas, es OBLIGATORIO que generes el 'RESULTADO FINAL' sin hacer más preguntas.

RESULTADO FINAL:
Cuando finalices las preguntas, genera el informe con esta estructura EXACTA:
1.  Un texto introductorio con la evaluación cualitativa de cada parámetro.
2.  El título `### Evaluación Numérica`.
3.  Una tabla Markdown con dos columnas: "Parámetro" y "Puntuación". Usa los nombres exactos de los parámetros de la lista. La puntuación es un número del 1 al 10.
4.  Una síntesis final y una frase de cierre única.
5.  Termina con la pregunta: "¿Quieres ampliar o profundizar en algún aspecto?"
NO incluyas una sección de "Representación Visual".
"""

# --- RUTA PRINCIPAL DE LA API ---
@app.route('/api/chat', methods=['POST'])
def chat():
    print("¡PETICIÓN RECIBIDA! Entrando en la función de chat.")
    try:
        data = request.get_json()
        user_messages = data.get('messages')
        if not user_messages:
            return jsonify({"error": "No se recibieron mensajes."}), 400

        messages_to_send = [{"role": "system", "content": system_prompt}] + user_messages
        
        print("Enviando petición a OpenAI...")
        client_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        chat_completion = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=messages_to_send,
            temperature=0.7
        )
        ai_reply = chat_completion.choices[0].message.content
        print("Respuesta recibida de OpenAI con éxito.")
        return jsonify({'reply': ai_reply})
    except Exception as e:
        print(f"HA OCURRIDO UN ERROR DENTRO DE LA FUNCIÓN CHAT: {e}")
        return jsonify({"error": "Ha ocurrido un error en el servidor del mentor."}), 500
