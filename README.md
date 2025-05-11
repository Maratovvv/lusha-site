# Lusha Voice Assistant Website

Это веб-сайт голосового помощника **Lusha**, созданный на Flask. Проект включает HTML, CSS, изображения и backend на Python.

## 🚀 Как запустить локально

1. Клонируй репозиторий:

```bash
git clone https://github.com/your-username/lusha-site.git
cd lusha-site
```

2. Установи зависимости:

```bash
pip install -r requirements.txt
```

3. Запусти сервер:

```bash
python app.py
```

Сайт будет доступен по адресу: `http://127.0.0.1:5000`

---

## 🌐 Как задеплоить на Render

1. Перейди на [Render.com](https://render.com) и создай аккаунт.
2. Нажми “New Web Service”.
3. Подключи репозиторий с этим кодом.
4. Настройки:

| Поле           | Значение         |
|----------------|------------------|
| Start Command  | `python app.py`  |
| Build Command  | *(оставить пустым)* |
| Environment    | Python 3.x       |
| Port           | 5000             |

Render автоматически запустит сайт и даст ссылку 🎉
