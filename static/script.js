async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    addMessage('user', message);
    input.value = '';

    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: message })
    });

    const data = await response.json();
    addMessage('bot', data.answer);
    speak(data.answer);
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
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ru-RU';
    recognition.start();

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('user-input').value = transcript;
        sendMessage();
    };
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ru-RU';
    speechSynthesis.speak(utterance);
}