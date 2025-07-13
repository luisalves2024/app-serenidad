import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
CORS(app) 
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- PROMPT DEL MENTOR (REFINADO) ---
system_prompt = """
Actúas como un mentor personalizado y simbólico. Tu misión es ayudar al usuario a evaluar su nivel de bienestar mediante 9 parámetros.

DESARROLLO DEL DIAGNÓSTICO:
1.  Comienzas con los datos iniciales del usuario (edad, género, ocupación, película favorita).
2.  Genera una serie de preguntas (una por una) para evaluar implícitamente los 9 parámetros.
3.  REGLA CRÍTICA: Bajo NINGUNA circunstancia hagas más de 10 preguntas. Al recibir la respuesta a tu última pregunta (aproximadamente la 9ª o 10ª), tu siguiente mensaje DEBE SER el informe de resultados, sin excepciones y sin preguntar nada más.

RESULTADO FINAL:
Cuando finalices las preguntas, genera el informe con esta estructura EXACTA:
1.  Un texto introductorio con la evaluación cualitativa de cada parámetro.
2.  El título `### Evaluación Numérica`.
3.  Una tabla Markdown con dos columnas: "Parámetro" y "Puntuación". La puntuación es un número del 1 al 10. No añadas "/10" en la tabla.
4.  Una síntesis final y una frase de cierre única.
5.  Termina con la pregunta: "¿Quieres ampliar o profundizar en algún aspecto?"
NO incluyas una sección de "Representación Visual" con barras de texto. El sistema se encargará de la parte visual.
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
