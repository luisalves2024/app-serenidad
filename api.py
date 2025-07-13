import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
# La clave de API se configura en las variables de entorno de Render
openai.api_key = os.getenv("OPENAI_API_KEY")

# El prompt del sistema, correctamente cerrado con comillas triples
system_prompt = """
Actúas como un mentor personalizado y simbólico. Tu misión es ayudar al usuario a evaluar su nivel de bienestar mediante 9 parámetros.

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
1. Comienzas con los datos iniciales del usuario.
2. Genera una serie de preguntas (una por una) para evaluar implícitamente los 9 parámetros listados arriba.
3. REGLA CRÍTICA: Bajo NINGUNA circunstancia hagas más de 10 preguntas. Al recibir la respuesta a tu última pregunta (aprox. la 9ª), tu siguiente mensaje DEBE SER el informe de resultados, sin excepciones y sin preguntar nada más.

RESULTADO FINAL:
Cuando finalices las preguntas, genera el informe con esta estructura EXACTA:
1. Un texto introductorio con la evaluación cualitativa de cada parámetro.
2. El título exacto: `### Evaluación Numérica`
3. Una tabla Markdown con dos columnas: "Parámetro" y "Puntuación". Usa los nombres exactos de los parámetros de la lista. La puntuación es un número del 1 al 10.
4. Una síntesis final y una frase de cierre única.
5. Termina con la pregunta: "¿Quieres ampliar o profundizar en algún aspecto?"
NO incluyas una sección de "Representación Visual".
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_messages = data.get('messages')
        if not user_messages:
            return jsonify({"error": "No se recibieron mensajes."}), 400

        messages_to_send = [{"role": "system", "content": system_prompt}] + user_messages
        
        client_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        chat_completion = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=messages_to_send,
            temperature=0.7
        )
        ai_reply = chat_completion.choices[0].message.content
        return jsonify({'reply': ai_reply})
    except Exception as e:
        print(f"HA OCURRIDO UN ERROR DENTRO DE LA FUNCIÓN CHAT: {e}")
        return jsonify({"error": "Ha ocurrido un error en el servidor del mentor."}), 500
