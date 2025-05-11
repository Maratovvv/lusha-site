from flask import Flask, render_template, jsonify, request
import random
import requests
from datetime import datetime
import pytz  # для часового пояса

app = Flask(__name__)

OWM_API_KEY = "4d7d7e1630b63b79c40e0d9ae002126b"

def get_weather(city_name):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={OWM_API_KEY}"
        geo_response = requests.get(geo_url, timeout=5).json()

        if not geo_response:
            return "Не могу найти такой город."

        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang=ru"
        weather_data = requests.get(weather_url, timeout=5).json()

        temp = weather_data['main']['temp']
        desc = weather_data['weather'][0]['description']
        wind = weather_data['wind']['speed']
        return f"{city_name.capitalize()}: {temp} градусов, {desc}, ветер {wind} м/с."
    except Exception as e:
        return f"Ошибка при получении погоды: {str(e)}"

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
            weather = get_weather(city)
            return jsonify({'answer': weather})
        else:
            return jsonify({'answer': 'Пожалуйста, уточни город.'})
    elif 'время' in question:
        tz = pytz.timezone('Asia/Bishkek')
        now = datetime.now(tz).strftime('%H:%M')
        return jsonify({'answer': f'В Бишкеке сейчас {now} (GMT+6)'})
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
