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
    
    // --- URL del Backend ---
    const BACKEND_URL = 'https://aplicacion-serenidad-backend.onrender.com/api/chat';

    // --- Manejador del formulario inicial ---
    inicioForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const edad = document.getElementById('edad').value;
        const genero = document.getElementById('genero').value;
        const ocupacion = document.getElementById('ocupacion').value;
        const pelicula = document.getElementById('pelicula').value;

        const primerMensaje = `El usuario tiene ${edad} años, su género es ${genero}, su ocupación es ${ocupacion} y su película favorita es "${pelicula}". Inicia la conversación.`;
        
        conversationHistory.push({ role: 'user', content: primerMensaje });

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
    function agregarMensaje(texto, remitente) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${remitente}-message`);
    
        if (remitente === 'ai' && texto.includes('| Parámetro')) {
            messageElement.innerHTML = generarHtmlDeResultados(texto);
        } else {
            messageElement.innerText = texto; 
        }
        
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // --- Función para transformar los resultados en barras de progreso ---
    function generarHtmlDeResultados(textoMarkdown) {
        const getColorForScore = (score) => {
            if (score <= 3) return '#5cb85c'; // Verde
            if (score <= 6) return '#f0ad4e'; // Amarillo
            if (score <= 10) return '#d9534f'; // Rojo
            return '#777';
        };

        let html = textoMarkdown;
        const regex = /\|\s*(.*?)\s*\|\s*(\d+)\s*\/10\s*\|/g;
        
        let tablaHtml = '<div class="resultados-container">';
        let match;
        while ((match = regex.exec(textoMarkdown)) !== null) {
            const parametro = match[1].trim();
            if (parametro.includes('---') || parametro.toLowerCase().includes('parámetro')) continue;

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

        const tablaMarkdownRegex = /Tabla de puntuación,[\s\S]*?(\n\n|$)/;
        html = html.replace(tablaMarkdownRegex, tablaHtml);

        const visualMarkdownRegex = /Representación visual[\s\S]*/;
        html = html.replace(visualMarkdownRegex, '');

        return html;
    }
});
