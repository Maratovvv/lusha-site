from flask import Flask, render_template, jsonify, request
import random
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

OWM_API_KEY = "4d7d7e1630b63b79c40e0d9ae002126b"  # временный ключ

def get_weather(city_name):
    try:
        if not city_name:
            return "Пожалуйста, укажи город. Например: погода в Бишкеке"

        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={OWM_API_KEY}"
        geo_response = requests.get(geo_url, timeout=5).json()

        if not isinstance(geo_response, list) or len(geo_response) == 0:
            return "Я не смогла найти такой город. Проверь написание и попробуй снова 😊"

        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang=ru"
        weather_data = requests.get(weather_url, timeout=5).json()

        temp = weather_data['main']['temp']
        desc = weather_data['weather'][0]['description']
        wind = weather_data['wind']['speed']
        return f"{city_name.capitalize()}: {temp}°C, {desc}, ветер {wind} м/с."

    except Exception as e:
        import traceback
        return f"Ошибка при получении погоды:\n{traceback.format_exc(limit=1)}"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').lower()

    if 'привет' in question:
        return jsonify({'answer': 'Привет! Чем могу помочь?'})
    elif 'как дела' in question:
        return jsonify({'answer': 'У меня всё отлично, спасибо!'})
    elif 'шутка' in question:
        jokes = [
            'Почему компьютер не может держать секреты? Потому что у него слишком много окон.',
            'Что сказал ноль восьмерке? Классный пояс!'
        ]
        return jsonify({'answer': random.choice(jokes)})
    elif 'погода в' in question:
        parts = question.split("погода в")
        if len(parts) > 1:
            city = parts[1].strip()
            if city:
                weather = get_weather(city)
                return jsonify({'answer': weather})
        return jsonify({'answer': 'Пожалуйста, укажи город. Например: погода в Бишкеке'})
    elif question.strip() == "погода":
        return jsonify({'answer': 'Уточни, в каком городе ты хочешь узнать погоду '})
    elif 'время' in question:
        tz = pytz.timezone('Asia/Bishkek')
        now = datetime.now(tz).strftime('%H:%M')
        return jsonify({'answer': f'В Бишкеке сейчас {now}'})
    elif 'дата' in question:
        date = datetime.now().strftime('%d.%m.%Y')
        return jsonify({'answer': f'Сегодня {date}'})
    elif 'стоп' in question:
        return jsonify({'answer': 'Хорошо, отключаюсь.'})
    else:
        smart_phrases = [
            "Интересная тема! Расскажи подробнее.",
            "Хм... любопытно. Давай разберёмся вместе!",
            "Это хороший вопрос. Я бы тоже хотела узнать больше.",
            "Поясни, пожалуйста, что именно ты хочешь узнать? 😊",
            "Это звучит как что-то важное. Расскажи подробнее!"
        ]
        return jsonify({'answer': random.choice(smart_phrases)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
