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
        const s = p.size / 2;
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

function sendQuestion() {
    const inputField = document.getElementById('inputText');
    const input = inputField.value.trim();
    if (!input) return;

    addMessage('user', input);
    inputField.value = '';

    if (/спасибо|благодарю|thank you/i.test(input)) {
        const thankReply = 'Пожалуйста! Всегда рада помочь 😊';
        addMessage('bot', thankReply);
        speak(thankReply);
        launchEffect('confetti'); // фантики
        return;
    }

    if (/молодец|класс|отлично|хорошо|замечательно|прекрасно/i.test(input)) {
        const praiseReply = 'Спасибо! Мне очень приятно 😊';
        addMessage('bot', praiseReply);
        speak(praiseReply);
        launchEffect('heart'); // сердечки
        return;
    }

    const typing = document.createElement('div');
    typing.id = 'typing';
    typing.className = 'bot';
    typing.innerText = 'Lusha печатает...';
    document.getElementById('chat-box').appendChild(typing);

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
    })
    .then(res => res.json())
    .then(data => {
        const typingBox = document.getElementById('typing');
        if (typingBox) typingBox.remove();

        addMessage('bot', data.answer);
        speak(data.answer);
    });
}

function quickAsk(text) {
    document.getElementById('inputText').value = text;
    sendQuestion();
}

function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ru-RU';
    recognition.start();
    recognition.onresult = function (event) {
        const text = event.results[0][0].transcript;
        document.getElementById('inputText').value = text;
        sendQuestion();
    };
}

function speak(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ru-RU';

    const logo = document.querySelector('.logo');
    if (logo) logo.classList.add('speaking');

    utterance.onend = () => {
        if (logo) logo.classList.remove('speaking');
    };

    synth.speak(utterance);
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
