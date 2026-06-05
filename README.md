# Аналіз захворювань — diploma-app

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yevhem/diploma-app/main)

Цей репозиторій містить Streamlit-додаток для аналізу кількості випадків інфекції гонореї.

## Розгорнути в Streamlit Cloud (швидко)
1. Увійди на https://streamlit.io/cloud через GitHub.
2. New app → вибери `yevhem/diploma-app`, гілку `main`, main file: `app.py` → Deploy.
3. Скопій посилання після розгортання і надішли його викладачу.

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
Головний файл: `app.py`. Потрібна допомога — напиши тут.