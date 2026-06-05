import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from src.models import get_all_models
from src.data_prep import load_and_prepare_data

# ==========================================
# КОНФІГУРАЦІЯ ТА СТИЛІ
# ==========================================
st.set_page_config(page_title="Gonorrhea Analysis", layout="wide")

COLOR_MAP = {
    "Фактичні дані": "#3498db",     # Синій
    "Poisson Regression": "#2ecc71", # Зелений
    "Random Forest": "#e74c3c",     # Червоний
    "XGBoost": "#f1c40f"            # Жовтий
}

DASH_MAP = {
    "Фактичні дані": "solid",
    "Історія (навчання моделі)": "dot",
    "Майбутній прогноз (12 міс)": "dash"
}

# Завантаження даних з перевіркою
@st.cache_data
def load_data():
    file_path = 'data/final_data.csv'
    # Дебаг: перевірка шляху, якщо файл не знайдено
    if not os.path.exists(file_path):
        st.error(f"ФАЙЛ НЕ ЗНАЙДЕНО: {file_path}")
        st.write(f"Поточна робоча директорія: {os.getcwd()}")
        st.write("Список файлів у папці:")
        st.write(os.listdir('.'))
        if os.path.exists('data'):
             st.write(f"Вміст папки data: {os.listdir('data')}")
        st.stop()
        
    try:
        df = pd.read_csv(file_path)
        df['month_dt'] = pd.to_datetime(df['month'])
        df['year'] = df['month_dt'].dt.year
        df['month_num'] = df['month_dt'].dt.month
        return df
    except Exception as e:
        st.error(f"Помилка завантаження даних: {e}")
        st.stop()

df = load_data()

# ==========================================
# НАВІГАЦІЯ
# ==========================================
st.sidebar.title("🛠 Навігація")
page = st.sidebar.radio("Перейти до:", ["📊 Графіки та Аналіз", "📈 Метрики моделей"])
st.sidebar.markdown("---")

# ==========================================
# СТОРІНКА 1: ГРАФІКИ
# ==========================================
if page == "📊 Графіки та Аналіз":
    st.title("📊 Аналіз інфекцій: Графіки")
    
    st.sidebar.header("Налаштування")
    show_actuals = st.sidebar.checkbox("Показувати фактичні дані", value=True)
    all_years = sorted(df['year'].unique())
    selected_years = st.sidebar.multiselect("Виберіть роки:", options=all_years, default=all_years[-2:])
    selected_model_names = st.sidebar.multiselect("Виберіть моделі:", options=list(get_all_models().keys()), default=[])
    show_future = st.sidebar.checkbox("Відображати майбутній прогноз (12 міс)", value=True)
    
    if not show_actuals and not selected_years and not selected_model_names:
        st.info("👈 Виберіть дані у бічній панелі для відображення.")
        st.stop()

    plot_rows = []

    # 1. Додаємо фактичні дані
    if show_actuals and selected_years:
        filtered = df[df['year'].isin(selected_years)].sort_values('month_dt')
        for _, row in filtered.iterrows():
            plot_rows.append({"Дата": row['month_dt'], "Випадки": row['case_count'], "Модель": "Фактичні дані", "Тип": "Фактичні дані"})

    # 2. Додаємо прогнози
    if selected_model_names:
        try:
            data_out = load_and_prepare_data('data/final_data.csv')
            X_train, y_train = data_out[0], data_out[1]
            last_act_date = df['month_dt'].iloc[-1]
            aligned_dates = df['month_dt'].iloc[-len(y_train):].tolist()
            
            models = get_all_models()
            for name in selected_model_names:
                model = models[name]
                model.fit(X_train, y_train)
                
                # Історія
                hist_preds = model.predict(X_train)
                for d, p in zip(aligned_dates, hist_preds):
                    if d.year in selected_years:
                        plot_rows.append({"Дата": d, "Випадки": p, "Модель": name, "Тип": "Історія (навчання моделі)"})
                
                # Майбутнє
                if show_future:
                    curr = df['case_count'].iloc[-1]
                    for i in range(1, 13):
                        p = model.predict(np.array([[curr]]))[0]
                        plot_rows.append({"Дата": last_act_date + pd.DateOffset(months=i), "Випадки": p, "Модель": name, "Тип": "Майбутній прогноз (12 міс)"})
                        curr = p
        except Exception as e:
            st.error(f"Помилка при роботі з моделями: {e}")

    if plot_rows:
        plot_df = pd.DataFrame(plot_rows)
        fig = px.line(plot_df, x="Дата", y="Випадки", color="Модель", line_dash="Тип", 
                      markers=True, color_discrete_map=COLOR_MAP, line_dash_map=DASH_MAP)
        fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# СТОРІНКА 2: МЕТРИКИ
# ==========================================
elif page == "📈 Метрики моделей":
    st.title("📈 Математична оцінка моделей")
    st.write("Розрахунок MAPE, MAE, MSE та RMSE на основі порівняння реальних даних із прогнозами моделей.")
    
    try:
        data_out = load_and_prepare_data('data/final_data.csv')
        X_eval, y_eval = data_out[0], data_out[1] 
        
        models = get_all_models()
        metrics_results = []
        predictions_dict = {"Реальні значення": y_eval.flatten() if hasattr(y_eval, 'flatten') else y_eval}
        
        for name, model in models.items():
            model.fit(X_eval, y_eval)
            preds = model.predict(X_eval)
            predictions_dict[f"Прогноз: {name}"] = preds
            
            mae = mean_absolute_error(y_eval, preds)
            mse = mean_squared_error(y_eval, preds)
            rmse = np.sqrt(mse)
            mape = mean_absolute_percentage_error(y_eval, preds) * 100
            
            metrics_results.append({
                "Модель": name,
                "MAPE (%)": round(mape, 2),
                "MAE": round(mae, 2),
                "MSE": round(mse, 2),
                "RMSE": round(rmse, 2)
            })
        
        st.subheader("Показники похибки")
        st.dataframe(pd.DataFrame(metrics_results), use_container_width=True)
        
        st.subheader("Таблиця: Реальні значення проти Прогнозу")
        preds_df = pd.DataFrame(predictions_dict)
        st.dataframe(preds_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Не вдалося розрахувати метрики: {e}")
