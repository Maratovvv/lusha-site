from flask import Flask, render_template, jsonify, request
import random
import requests
from datetime import datetime
import pytz
import traceback
import re

app = Flask(__name__)

OWM_API_KEY = "dbf1c332caec3ca0dc92ec2136609b42"

def get_weather(city_name, lang='ru'):
    try:
        if not city_name:
            if lang.startswith('en'):
                return "Please specify a city. For example: weather in Bishkek"
            return "Пожалуйста, укажи город. Например: погода в Бишкеке"

        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={OWM_API_KEY}"
        geo_response = requests.get(geo_url, timeout=5).json()

        if not isinstance(geo_response, list) or len(geo_response) == 0:
            if lang.startswith('en'):
                return "I couldn't find such a city. Please check the spelling and try again 😊"
            return "Я не смогла найти такой город. Проверь написание и попробуй снова 😊"

        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang={lang[:2]}"
        weather_data = requests.get(weather_url, timeout=5).json()

        temp = weather_data['main']['temp']
        desc = weather_data['weather'][0]['description']
        wind = weather_data['wind']['speed']
        if lang.startswith('en'):
            return f"{city_name.capitalize()}: {temp}°C, {desc}, wind {wind} m/s."
        return f"{city_name.capitalize()}: {temp}°C, {desc}, ветер {wind} м/с."

    except Exception:
        return f"Ошибка при получении погоды:\n{traceback.format_exc(limit=1)}"

def get_exchange_rate(currency_code, lang='ru'):
    try:
        url = "https://open.er-api.com/v6/latest/KGS"
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            if lang.startswith('en'):
                return "Cannot get exchange rates now."
            return "Не могу получить курс валют."
        data = res.json()
        rates = data.get('rates', {})
        rate = rates.get(currency_code)
        if not rate:
            if lang.startswith('en'):
                return "Exchange rate not found."
            return "Курс не найден."
        exchange_rate = 1 / rate
        if lang.startswith('en'):
            return f"Current {currency_code} exchange rate to som: {exchange_rate:.2f}"
        return f"Текущий курс {currency_code} к сому: {exchange_rate:.2f}"
    except Exception:
        return f"Ошибка при получении курса валют:\n{traceback.format_exc(limit=1)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').lower()
    lang = data.get('lang', 'ru-RU').lower()

    if any(word in question for word in ['привет', 'здравствуй', 'hello']):
        if lang.startswith('en'):
            return jsonify({'answer': 'Hello! How can I help you?'})
        return jsonify({'answer': 'Привет! Чем могу помочь?'})

    if any(word in question for word in ['как дела', 'как ты']):
        if lang.startswith('en'):
            return jsonify({'answer': "I'm doing great, thank you!"})
        return jsonify({'answer': 'У меня всё отлично, спасибо!'})

    if any(word in question for word in ['шутка', 'расскажи шутку', 'анекдот', 'joke']):
        jokes_ru = [
            'Почему компьютер не может держать секреты? Потому что у него слишком много окон.',
            'Что сказал ноль восьмерке? Классный пояс!',
            'Почему программисты любят кофе? Потому что без него нет кода!'
        ]
        jokes_en = [
            'Why can’t computers keep secrets? Because they have too many windows.',
            'What did zero say to eight? Nice belt!',
            'Why do programmers love coffee? Because without it, there is no code!'
        ]
        if lang.startswith('en'):
            return jsonify({'answer': random.choice(jokes_en)})
        return jsonify({'answer': random.choice(jokes_ru)})

    if 'погода' in question or 'weather' in question:
        city_match = re.search(r'погода в ([а-яА-ЯёЁ\s\-]+)', question)
        if not city_match:
            city_match = re.search(r'weather in ([a-zA-Z\s\-]+)', question)
        city = city_match.group(1).strip() if city_match else ''
        if city:
            weather = get_weather(city, lang)
            return jsonify({'answer': weather})
        if lang.startswith('en'):
            return jsonify({'answer': 'Please specify the city for the weather forecast. For example: weather in Bishkek'})
        return jsonify({'answer': 'Пожалуйста, укажи город для прогноза погоды. Например: погода в Бишкеке'})

    if any(word in question for word in ['курс доллара', 'курс usd', 'курс доллар', 'usd rate', 'dollar rate']):
        rate = get_exchange_rate('USD', lang)
        return jsonify({'answer': rate})

    if any(word in question for word in ['курс евро', 'курс eur', 'курс евро', 'eur rate', 'euro rate']):
        rate = get_exchange_rate('EUR', lang)
        return jsonify({'answer': rate})

    if any(word in question for word in ['время', 'который час', 'time']):
        tz = pytz.timezone('Asia/Bishkek')
        now = datetime.now(tz).strftime('%H:%M')
        if lang.startswith('en'):
            return jsonify({'answer': f'Current time in Bishkek is {now}'})
        return jsonify({'answer': f'В Бишкеке сейчас {now}'})

    if any(word in question for word in ['дата', 'какое число', 'число', 'date']):
        date = datetime.now().strftime('%d.%m.%Y')
        if lang.startswith('en'):
            return jsonify({'answer': f'Today is {date}'})
        return jsonify({'answer': f'Сегодня {date}'})

    if any(word in question for word in ['стоп', 'выключись', 'закрой', 'stop']):
        if lang.startswith('en'):
            return jsonify({'answer': 'Okay, shutting down.'})
        return jsonify({'answer': 'Хорошо, отключаюсь.'})

    smart_phrases_ru = [
        "Интересная тема! Расскажи подробнее.",
        "Хм... любопытно. Давай разберёмся вместе!",
        "Это хороший вопрос. Я бы тоже хотела узнать больше.",
        "Поясни, пожалуйста, что именно ты хочешь узнать?",
        "Это звучит как что-то важное. Расскажи подробнее!"
    ]
    smart_phrases_en = [
        "Interesting topic! Tell me more.",
        "Hmm... curious. Let's figure it out together!",
        "That's a good question. I'd like to know more too.",
        "Please explain what exactly you want to know?",
        "This sounds important. Tell me more!"
    ]

    if lang.startswith('en'):
        return jsonify({'answer': random.choice(smart_phrases_en)})
    return jsonify({'answer': random.choice(smart_phrases_ru)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
