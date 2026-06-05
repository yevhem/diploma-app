# Аналіз захворювань — diploma-app

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yevhem/diploma-app/main)

Цей репозиторій містить Streamlit-додаток для аналізу кількості випадків інфекції гонореї.

## Розгорнути в Streamlit Cloud (швидко)
1. Відкрийте https://streamlit.io/cloud і авторизуйтесь через GitHub.
2. Натисніть **New app** → виберіть репозиторій `yevhem/diploma-app`, гілку `main` і вкажіть `app.py` як основний файл.
3. Після першого розгортання Streamlit Cloud автоматично запустить додаток — скопіюйте отримане посилання і надішліть викладачу.

Примітка: бейдж вище веде на очікуваний `share.streamlit.io/yevhem/diploma-app/main` — він працюватиме як тільки ви або я розгорнемо додаток у Streamlit Cloud.

## Локально (якщо потрібно)
Щоб швидко перевірити локально:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Потім відкрийте `http://localhost:8501`.

## Коментарі
- Головний файл: `app.py`.
- Всі залежності описані в `requirements.txt`.
- Якщо хочеш, я можу пройти з тобою кроки деплою в Streamlit Cloud та підключити додаток (треба авторизуватися у своєму акаунті). 