import os
import openai
import gspread
import re
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
CORS(app) 
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
try:
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    
    # Esta línea lee las credenciales del archivo secreto que subiste a Render
    creds_json_str = os.getenv("GCP_CREDENTIALS_JSON")
    if creds_json_str:
        creds_dict = eval(creds_json_str)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Asegúrate de que el nombre "Resultados Serenidad" coincide exactamente con el de tu hoja
        sheet = client.open("Resultados Serenidad").sheet1 
        print("Conexión con Google Sheets exitosa.")
    else:
        sheet = None
        print("Advertencia: No se encontraron las credenciales de Google Cloud. La función de guardado está desactivada.")

except Exception as e:
    print(f"Error al conectar con Google Sheets: {e}")
    sheet = None

# --- PROMPT DEL MENTOR ---
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

# --- FUNCIÓN PARA GUARDAR DATOS EN GOOGLE SHEETS ---
def guardar_resultados(texto_informe, datos_iniciales):
    if not sheet:
        print("No se pueden guardar los resultados, la conexión a Sheets está inactiva.")
        return

    try:
        puntuaciones_dict = {p[0].strip(): int(p[1]) for p in re.findall(r"\|\s*(.*?)\s*\|\s*(\d+)\s*/10\s*\|", texto_informe)}
        
        if not puntuaciones_dict:
            print("No se encontraron puntuaciones en el formato esperado.")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # El orden debe coincidir con las columnas de tu hoja de cálculo
        fila = [
            now,
            datos_iniciales.get('edad'),
            datos_iniciales.get('genero'),
            datos_iniciales.get('ocupacion'),
            datos_iniciales.get('pelicula'),
            puntuaciones_dict.get('Autocuidado limitado'),
            puntuaciones_dict.get('Mente sin pausa'),
            puntuaciones_dict.get('Exigencia interna crónica'),
            puntuaciones_dict.get('Esfuerzo no reconocido'),
            puntuaciones_dict.get('Soledad en la cima'),
            puntuaciones_dict.get('Sobrecarga tecnológica'),
            puntuaciones_dict.get('Conciliación desequilibrada'),
            puntuaciones_dict.get('Maternidad penalizada'),
            puntuaciones_dict.get('Ausencia de espacios de recarga')
        ]
        sheet.append_row(fila)
        print("Resultados guardados correctamente en Google Sheets.")
    
    except Exception as e:
        print(f"Error durante el guardado en Google Sheets: {e}")

# --- RUTA PRINCIPAL DE LA API ---
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

        if "| Parámetro" in ai_reply and "Puntuación /10" in ai_reply:
            # Extraer los datos iniciales del primer mensaje del usuario
            primer_mensaje = user_messages[0]['content'] if user_messages else ''
            datos_iniciales = {
                'edad': re.search(r'edad (\d+)', primer_mensaje, re.I).group(1) if re.search(r'edad (\d+)', primer_mensaje, re.I) else None,
                'genero': re.search(r'género es (.*?),', primer_mensaje, re.I).group(1) if re.search(r'género es (.*?),', primer_mensaje, re.I) else None,
                'ocupacion': re.search(r'ocupación es (.*?) y', primer_mensaje, re.I).group(1) if re.search(r'ocupación es (.*?) y', primer_mensaje, re.I) else None,
                'pelicula': re.search(r'película favorita es "(.*?)"', primer_mensaje, re.I).group(1) if re.search(r'película favorita es "(.*?)"', primer_mensaje, re.I) else None
            }
            guardar_resultados(ai_reply, datos_iniciales)

        return jsonify({'reply': ai_reply})

    except Exception as e:
        print(f"Ha ocurrido un error en el chat: {e}")
        return jsonify({"error": "Ha ocurrido un error en el servidor del mentor."}), 500
