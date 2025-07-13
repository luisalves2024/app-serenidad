document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a los elementos del DOM ---
    const inicioContainer = document.getElementById('inicio-container');
    const chatContainer = document.getElementById('chat-container');
    const inicioForm = document.getElementById('inicio-form');
    const chatForm = document.getElementById('chat-form');
    const chatLog = document.getElementById('chat-log');
    const userInput = document.getElementById('user-input');
    const loadingIndicator = document.getElementById('loading');

    // --- Estado de la Conversación ---
    let conversationHistory = [];
    
    // --- URL del Backend (la cambiaremos después) ---
    const BACKEND_URL = 'https://app-serenidad-backend.onrender.com/api/chat'; // ¡Importante! Esto es un placeholder.

    // --- Manejador del formulario inicial ---
    inicioForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const edad = document.getElementById('edad').value;
        const genero = document.getElementById('genero').value;
        const ocupacion = document.getElementById('ocupacion').value;
        const pelicula = document.getElementById('pelicula').value;

        // Preparamos el primer mensaje para la IA
        const primerMensaje = `El usuario tiene ${edad} años, su género es ${genero}, su ocupación es ${ocupacion} y su película favorita es "${pelicula}". Inicia la conversación.`;
        
        conversationHistory.push({ role: 'user', content: primerMensaje });

        // Cambiamos de vista
        inicioContainer.classList.add('hidden');
        chatContainer.classList.remove('hidden');

        enviarConversacionAlBackend();
    });

    // --- Manejador del formulario del chat ---
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const userMessage = userInput.value.trim();
        if (userMessage) {
            agregarMensaje(userMessage, 'user');
            conversationHistory.push({ role: 'user', content: userMessage });
            userInput.value = '';
            enviarConversacionAlBackend();
        }
    });

    // --- Función para enviar datos al backend ---
    async function enviarConversacionAlBackend() {
        loadingIndicator.classList.remove('hidden');
        chatForm.classList.add('hidden');

        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: conversationHistory })
            });

            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.statusText}`);
            }

            const data = await response.json();
            const aiMessage = data.reply;
            
            // Usamos un pequeño retraso para que la respuesta no se sienta tan instantánea
            setTimeout(() => {
                loadingIndicator.classList.add('hidden');
                agregarMensaje(aiMessage, 'ai');
                conversationHistory.push({ role: 'assistant', content: aiMessage });
                chatForm.classList.remove('hidden');
                userInput.focus();
            }, 500);

        } catch (error) {
            loadingIndicator.classList.add('hidden');
            chatForm.classList.remove('hidden');
            agregarMensaje('Lo siento, ha ocurrido un error de conexión con el mentor. Por favor, intenta de nuevo más tarde.', 'ai');
            console.error("Error al contactar el backend:", error);
        }
    }

    // --- Función de ayuda para añadir mensajes al log ---
    function // REEMPLAZA TU FUNCIÓN ACTUAL CON ESTA
function agregarMensaje(texto, remitente) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${remitente}-message`);

    // ¡Aquí está la magia!
    // Si el mensaje es del asistente y contiene la tabla de resultados...
    if (remitente === 'ai' && texto.includes('| Parámetro')) {
        // ...lo transformamos en HTML visual.
        messageElement.innerHTML = generarHtmlDeResultados(texto);
    } else {
        // Si no, lo mostramos como texto normal.
        messageElement.innerText = texto; 
    }

    chatLog.appendChild(messageElement);
    chatLog.scrollTop = chatLog.scrollHeight; // Auto-scroll hacia abajo
}

// AÑADE ESTA NUEVA FUNCIÓN JUSTO DEBAJO DE LA ANTERIOR
function generarHtmlDeResultados(textoMarkdown) {
    // Función para asignar un color según la puntuación (0-3 verde, 4-6 amarillo, 7-10 rojo)
    const getColorForScore = (score) => {
        if (score <= 3) return '#5cb85c'; // Verde
        if (score <= 6) return '#f0ad4e'; // Amarillo
        if (score <= 10) return '#d9534f'; // Rojo
        return '#777';
    };

    let html = textoMarkdown;
    // Regex para encontrar las líneas de la tabla Markdown: | Parámetro | Puntuación /10 |
    const regex = /\|\s*(.*?)\s*\|\s*(\d+)\s*\/10\s*\|/g;

    let tablaHtml = '<div class="resultados-container">';
    let match;
    while ((match = regex.exec(textoMarkdown)) !== null) {
        const parametro = match[1].trim();
        const puntuacion = parseInt(match[2], 10);
        const color = getColorForScore(puntuacion);

        tablaHtml += `
            <div class="resultado-item">
                <span class="parametro-label">${parametro} (${puntuacion}/10)</span>
                <div class="barra-progreso-contenedor">
                    <div class="barra-progreso-relleno" style="width: ${puntuacion * 10}%; background-color: ${color};"></div>
                </div>
            </div>
        `;
    }
    tablaHtml += '</div>';

    // Reemplazamos la tabla Markdown original y la visual de texto por nuestro nuevo HTML
    html = html.replace(regex, ''); // Elimina las filas de la tabla ya procesadas
    html = html.replace(/\| Puntuación \/10\s*\|/g, '');
    html = html.replace(/\|-----------------\|/g, '');
    html = html.replace(/\|\s*VALOR\s*\|\s*VISUAL\s*\|/g, ''); // Elimina cabeceras extra
    html = html.replace(/\|\s*.*?/g, ''); // Elimina cualquier resto de tabla

    // Inserta nuestro gráfico de barras en el lugar correcto
    return html.replace(/Tabla de puntuación,.*?\n/, tablaHtml);
}
});
