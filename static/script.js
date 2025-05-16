document.getElementById('inputText').focus();
document.getElementById('inputText').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') sendQuestion();
});

const canvas = document.getElementById('effect-canvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

function createParticles(type) {
    const particlesCount = 100;
    const particles = [];

    for (let i = 0; i < particlesCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            size: type === 'heart' ? (Math.random() * 15 + 10) : (Math.random() * 8 + 5),
            speedY: Math.random() * 3 + 2,
            speedX: (Math.random() - 0.5) * 2,
            rotation: Math.random() * 360,
            rotationSpeed: (Math.random() - 0.5) * 10,
            type: type,
            color: `hsl(${Math.random() * 360}, 100%, 70%)`
        });
    }
    return particles;
}

function drawParticle(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rotation * Math.PI / 180);

    if (p.type === 'confetti') {
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
    } else if (p.type === 'heart') {
        ctx.fillStyle = 'red';
        const s = p.size * 1.5;
        ctx.beginPath();
        ctx.moveTo(0, s);
        ctx.bezierCurveTo(0, s - s * 1.2, -s, s - s * 1.2, -s, s / 3);
        ctx.bezierCurveTo(-s, 0, 0, 0, 0, s / 3);
        ctx.bezierCurveTo(0, 0, s, 0, s, s / 3);
        ctx.bezierCurveTo(s, s - s * 1.2, 0, s - s * 1.2, 0, s);
        ctx.closePath();
        ctx.fill();
    }

    ctx.restore();
}

function animateParticles(particles) {
    let animationId;
    canvas.classList.add('active');

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            p.y += p.speedY;
            p.x += p.speedX;
            p.rotation += p.rotationSpeed;

            if (p.y > canvas.height) {
                p.y = -p.size;
                p.x = Math.random() * canvas.width;
            }
            drawParticle(p);
        });

        animationId = requestAnimationFrame(animate);
    }

    animate();

    setTimeout(() => {
        cancelAnimationFrame(animationId);
        canvas.classList.remove('active');
        setTimeout(() => ctx.clearRect(0, 0, canvas.width, canvas.height), 500);
    }, 5000);
}

function launchEffect(type) {
    const particles = createParticles(type);
    animateParticles(particles);
}

function addMessage(sender, text) {
    const box = document.getElementById('chat-box');
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper ' + sender;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.style.backgroundImage =
        sender === 'bot' ? "url('/static/logo1.png')" : "url('/static/user.png')";

    const msg = document.createElement('div');
    msg.className = 'message ' + sender;
    msg.innerText = text;

    wrapper.appendChild(avatar);
    wrapper.appendChild(msg);
    box.appendChild(wrapper);
    box.scrollTop = box.scrollHeight;
}

// Голосовой синтез с выбором женского голоса
const synth = window.speechSynthesis;
let voices = [];

function populateVoices() {
    voices = synth.getVoices();
}
populateVoices();
if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = populateVoices;
}

function speak(text, lang = 'ru-RU') {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;

    // Ищем женский голос по языку
    const femaleVoices = voices.filter(v =>
        v.lang.startsWith(lang) &&
        /female|woman|женский|google/i.test(v.name)
    );

    if (femaleVoices.length > 0) {
        utterance.voice = femaleVoices[0];
    } else {
        // Если нет женских — берем любой подходящий голос
        const voice = voices.find(v => v.lang.startsWith(lang));
        if (voice) utterance.voice = voice;
    }

    synth.speak(utterance);
}

function sendQuestion() {
    const inputField = document.getElementById('inputText');
    const input = inputField.value.trim();
    if (!input) return;

    const lang = document.getElementById('language-select')?.value || 'ru-RU';

    addMessage('user', input);
    inputField.value = '';

    if (/спасибо|благодарю|thank you/i.test(input)) {
        const thankReply = lang.startsWith('en') ? 'You are welcome! Always happy to help 😊' : 'Пожалуйста! Всегда рада помочь 😊';
        addMessage('bot', thankReply);
        speak(thankReply, lang);
        launchEffect('confetti');
        return;
    }

    if (/молодец|класс|отлично|хорошо|замечательно|прекрасно/i.test(input)) {
        const praiseReply = lang.startsWith('en') ? 'Thank you! I am very glad 😊' : 'Спасибо! Мне очень приятно 😊';
        addMessage('bot', praiseReply);
        speak(praiseReply, lang);
        launchEffect('heart');
        return;
    }

    const typing = document.createElement('div');
    typing.id = 'typing';
    typing.className = 'bot';
    typing.innerText = lang.startsWith('en') ? 'Lusha is typing...' : 'Lusha печатает...';
    document.getElementById('chat-box').appendChild(typing);

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input, lang: lang }),
    })
        .then(res => res.json())
        .then(data => {
            const typingBox = document.getElementById('typing');
            if (typingBox) typingBox.remove();

            addMessage('bot', data.answer);
            speak(data.answer, lang);
        });
}

function quickAsk(text) {
    document.getElementById('inputText').value = text;
    sendQuestion();
}

function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    const lang = document.getElementById('language-select')?.value || 'ru-RU';
    recognition.lang = lang;
    recognition.start();
    recognition.onresult = function (event) {
        const text = event.results[0][0].transcript;
        document.getElementById('inputText').value = text;
        sendQuestion();
    };
}

function clearChat() {
    document.getElementById('chat-box').innerHTML = '';
    document.getElementById('inputText').focus();
}

document.addEventListener('DOMContentLoaded', () => {
    const clickSound = document.getElementById('click-sound');
    document.querySelectorAll('button').forEach((btn) => {
        btn.addEventListener('click', () => {
            clickSound.currentTime = 0;
            clickSound.play();
        });
    });
});

window.addEventListener('load', () => {
    const greeting = 'Привет! Я Луша. Чем могу помочь?';
    addMessage('bot', greeting);
    speak(greeting);
});
