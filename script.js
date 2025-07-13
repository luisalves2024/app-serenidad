document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a los elementos del DOM ---
    const inicioContainer = document.getElementById('inicio-container');
    const chatContainer = document.getElementById('chat-container');
    const inicioForm = document.getElementById('inicio-form');
    const chatForm = document.getElementById('chat-form');
    const chatLog = document.getElementById('chat-log');
    const userInput = document.getElementById('user-input');
    const loadingIndicator = document.getElementById('loading');

    // --- ¡AQUÍ ESTÁ LA LÍNEA QUE FALTABA! ---
    let conversationHistory = []; 
    
    // --- URL del Backend ---
    const BACKEND_URL = 'https://app-serenidad-backend.onrender.com/api/chat';

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
        messageElement.innerText = texto; 
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    }
});
