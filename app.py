from flask import Flask, render_template, jsonify, request
import random
import requests
from datetime import datetime, timezone, timedelta
import pytz
import traceback
import re
import feedparser  # добавлен импорт

app = Flask(__name__)

OWM_API_KEY = "dbf1c332caec3ca0dc92ec2136609b42"
# NEWSAPI_API_KEY больше не нужен — удалён

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

    except Exception:
        return f"Ошибка при получении погоды:\n{traceback.format_exc(limit=1)}"


def get_kg_news(days_limit=3):
    try:
        feed_url = "https://kloop.kg/feed/"
        feed = feedparser.parse(feed_url)
        entries = feed.entries
        if not entries:
            return "Новостей нет."

        news_list = []
        now = datetime.now(timezone.utc)
        limit_date = now - timedelta(days=days_limit)

        for entry in entries:
            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            else:
                continue
            if published >= limit_date:
                news_list.append(f"- {entry.title}")
            if len(news_list) >= 5:
                break

        if not news_list:
            return f"За последние {days_limit} дня(ей) новостей не найдено."

        return "Последние новости Кыргызстана:\n" + "\n".join(news_list)
    except Exception:
        return f"Ошибка при получении новостей:\n{traceback.format_exc(limit=1)}"


def get_exchange_rate(currency_code):
    try:
        url = "https://open.er-api.com/v6/latest/KGS"
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return "Не могу получить курс валют."
        data = res.json()
        rates = data.get('rates', {})
        rate = rates.get(currency_code)
        if not rate:
            return "Курс не найден."
        exchange_rate = 1 / rate
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

    if any(word in question for word in ['привет', 'здравствуй', 'hello']):
        return jsonify({'answer': 'Привет! Чем могу помочь?'})

    if any(word in question for word in ['как дела', 'как ты']):
        return jsonify({'answer': 'У меня всё отлично, спасибо!'})

    if any(word in question for word in ['шутка', 'расскажи шутку', 'анекдот']):
        jokes = [
            'Почему компьютер не может держать секреты? Потому что у него слишком много окон.',
            'Что сказал ноль восьмерке? Классный пояс!',
            'Почему программисты любят кофе? Потому что без него нет кода!'
        ]
        return jsonify({'answer': random.choice(jokes)})

    if 'погода' in question:
        city_match = re.search(r'погода в ([а-яА-ЯёЁ\s\-]+)', question)
        city = city_match.group(1).strip() if city_match else ''
        if city:
            weather = get_weather(city)
            return jsonify({'answer': weather})
        else:
            return jsonify({'answer': 'Пожалуйста, укажи город для прогноза погоды. Например: погода в Бишкеке'})

    # Новые новости Кыргызстана из RSS
    if any(word in question for word in ['новости кыргызстана', 'новости кг', 'новости киргизии']):
        news = get_kg_news()
        return jsonify({'answer': news})

    if any(word in question for word in ['курс доллара', 'курс usd', 'курс доллар']):
        rate = get_exchange_rate('USD')
        return jsonify({'answer': rate})

    if any(word in question for word in ['курс евро', 'курс eur', 'курс евро']):
        rate = get_exchange_rate('EUR')
        return jsonify({'answer': rate})

    if any(word in question for word in ['время', 'который час']):
        tz = pytz.timezone('Asia/Bishkek')
        now = datetime.now(tz).strftime('%H:%M')
        return jsonify({'answer': f'В Бишкеке сейчас {now}'})

    if any(word in question for word in ['дата', 'какое число', 'число']):
        date = datetime.now().strftime('%d.%m.%Y')
        return jsonify({'answer': f'Сегодня {date}'})

    if any(word in question for word in ['стоп', 'выключись', 'закрой']):
        return jsonify({'answer': 'Хорошо, отключаюсь.'})

    smart_phrases = [
        "Интересная тема! Расскажи подробнее.",
        "Хм... любопытно. Давай разберёмся вместе!",
        "Это хороший вопрос. Я бы тоже хотела узнать больше.",
        "Поясни, пожалуйста, что именно ты хочешь узнать?",
        "Это звучит как что-то важное. Расскажи подробнее!"
    ]
    return jsonify({'answer': random.choice(smart_phrases)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
