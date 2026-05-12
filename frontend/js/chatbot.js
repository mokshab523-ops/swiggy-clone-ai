// Chatbot Functionality
let chatHistory = [];

function sendChatMessage() {
    const input = document.getElementById('chatbot-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Display user message
    appendChatMessage(message, 'user');
    input.value = '';
    
    if (!isAuthenticated()) {
        appendChatMessage('Please login to use chat support', 'bot');
        return;
    }
    
    showLoader(true);
    
    // Send message to chatbot API
    sendChatMessage(message)
        .then(response => {
            showLoader(false);
            appendChatMessage(response.bot_response, 'bot');
        })
        .catch(error => {
            showLoader(false);
            console.error('Chat error:', error);
            appendChatMessage('Sorry, I\'m having trouble responding. Please try again.', 'bot');
        });
}

function appendChatMessage(message, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');
    if (!messagesContainer) return;
    
    const messageEl = document.createElement('div');
    messageEl.className = `${sender}-message`;
    messageEl.textContent = message;
    
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showChatbotQuickReply(type) {
    const input = document.getElementById('chatbot-input');
    
    const replies = {
        'track': 'Can you help me track my order?',
        'refund': 'I want to request a refund',
        'help': 'What are the available features?',
        'recommend': 'Can you recommend some restaurants?'
    };
    
    if (input && replies[type]) {
        input.value = replies[type];
        input.focus();
    }
}

// Event listeners for chatbot
document.addEventListener('DOMContentLoaded', () => {
    const chatbotSendBtn = document.getElementById('chatbot-send');
    const chatbotInput = document.getElementById('chatbot-input');
    
    if (chatbotSendBtn) {
        chatbotSendBtn.addEventListener('click', sendChatMessage);
    }
    
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
    
    // Show initial message
    const messagesContainer = document.getElementById('chatbot-messages');
    if (messagesContainer && messagesContainer.children.length <= 1) {
        appendChatMessage('Hi! 👋 How can I help you today?', 'bot');
    }
});

// Voice ordering placeholder
function startVoiceOrdering() {
    if (!('webkitSpeechRecognition' in window)) {
        showToast('Voice recognition not supported in your browser', 'warning');
        return;
    }
    
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-IN';
    
    recognition.onstart = () => {
        showToast('Listening...', 'info');
    };
    
    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        
        // Send voice input as chat message
        document.getElementById('chatbot-input').value = transcript;
        sendChatMessage();
    };
    
    recognition.onerror = (event) => {
        showToast('Voice recognition error: ' + event.error, 'error');
    };
    
    recognition.start();
}