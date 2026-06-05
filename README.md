# Аналіз захворювань — diploma-app

Цей репозиторій містить Streamlit-додаток для аналізу кількості випадків інфекції гонореї.

## Швидко: розгорнути в Streamlit Cloud (одним кліком)
1. Відкрийте https://streamlit.io/cloud і авторизуйтесь через GitHub.
2. Натисніть **New app** → виберіть репозиторій `yevhem/diploma-app` і гілку `main`, як `Main file` вкажіть `app.py`.
3. Streamlit Cloud автоматично встановить залежності з `requirements.txt` і запустить додаток. Після цього буде доступне публічне посилання, яке можна скинути викладачу.

> Підказка: в README можна додати кнопку для швидкого відкриття, але самостійного деплою через кнопку без авторизації зробити не вдасться — потрібен аккаунт Streamlit.

### Шаблон кнопки (після розгортання можна замінити посилання на фактичне):

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yevhem/diploma-app/main)

## Локально (якщо потрібно)
Якщо потрібно запустити локально (тільки для перевірки):

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
- Якщо хочете, я можу допомогти розгорнути додаток у Streamlit Cloud і підготувати публічне посилання (потрібен доступ до вашого акаунта Streamlit / GitHub).