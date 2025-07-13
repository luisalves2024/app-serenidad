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
    const BACKEND_URL = 'https://app-serenidad-backend.onrender.com/api/chat';

    // --- Manejadores de Formularios ---
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

    // --- Funciones Principales ---
    async function enviarConversacionAlBackend() {
        loadingIndicator.classList.remove('hidden');
        chatForm.classList.add('hidden');
        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: conversationHistory })
            });
            if (!response.ok) throw new Error(`Error del servidor: ${response.statusText}`);
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

    function agregarMensaje(texto, remitente) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${remitente}-message`);

        if (remitente === 'ai' && texto.includes('### Evaluación Numérica')) {
            messageElement.innerHTML = generarHtmlDeResultados(texto);
        } else {
            messageElement.innerText = texto; 
        }

        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function generarHtmlDeResultados(textoMarkdown) {
        const getColorForScore = (score) => {
            if (score <= 3) return '#5cb85c'; // Verde
            if (score <= 6) return '#f0ad4e'; // Naranja
            if (score <= 10) return '#d9534f'; // Rojo
            return '#777';
        };

        let partes = textoMarkdown.split('### Evaluación Numérica');
        let textoIntroductorio = partes[0];
        let restoDelTexto = partes[1] || '';

        const regex = /\|\s*(.*?)\s*\|\s*(\d+|N\/A)\s*\|/g;

        let tablaHtml = '<h3>Evaluación Numérica</h3><div class="resultados-container">';
        let match;
        while ((match = regex.exec(restoDelTexto)) !== null) {
            const parametro = match[1].trim();
            if (parametro.includes('---') || parametro.toLowerCase().includes('parámetro')) continue;

            const puntuacionRaw = match[2].trim();
            if (puntuacionRaw.toLowerCase() === 'n/a') continue;

            const puntuacion = parseInt(puntuacionRaw, 10);
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
        tablaHtml += '<p class="leyenda-resultados">(Escala 0-10: 0 es equilibrio total, 10 es sobrecarga extrema)</p>';

        let textoFinal = restoDelTexto.replace(/\|[\s\S]*/, '');

        return textoIntroductorio + tablaHtml + textoFinal;
    }
});
