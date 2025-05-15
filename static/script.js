async function sendMessage() {
    const input = document.getElementById('user-input'); 
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    addMessage('user', message);
    input.value = '';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: message })
        });

        const data = await response.json();
        addMessage('bot', data.answer);
        speak(data.answer);
    } catch (error) {
        console.error('Ошибка при отправке сообщения:', error);
        addMessage('bot', 'Извините, произошла ошибка при обработке запроса.');
    }
}

function addMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = sender;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function startRecognition() {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        alert('Ваш браузер не поддерживает распознавание речи');
        return;
    }

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ru-RU';

    recognition.start();

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('user-input'); 
        if (input) {
            input.value = transcript;
            sendMessage();
        }
    };

    recognition.onerror = function(event) {
        console.error('Ошибка распознавания речи:', event.error);
        alert('Ошибка распознавания речи: ' + event.error);
    };
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ru-RU';
    speechSynthesis.speak(utterance);
}

document.addEventListener('DOMContentLoaded', () => {
    const clickSound = document.getElementById('click-sound');
    if (!clickSound) return;

    document.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            clickSound.currentTime = 0;
            clickSound.play();
        });
    });
});
