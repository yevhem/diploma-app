import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from statsmodels.tsa.seasonal import seasonal_decompose
from scr.models import get_all_models
from scr.data_prep import load_and_prepare_data

# ==========================================
# КОНФІГУРАЦІЯ ТА СТИЛІ
# ==========================================
st.set_page_config(page_title="Аналіз гонореї", page_icon="🦠", layout="wide")

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
    file_path = 'final_data.csv'
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
page = st.sidebar.radio("Перейти до:", ["📊 Аналіз гонореї", "📊 Сезонна декомпозиція", "📊 Аналіз кореляції", "📈 Метрики моделей"])
st.sidebar.markdown("---")

# ==========================================
# СТОРІНКА 1: ГРАФІКИ
# ==========================================
if page == "📊 Аналіз гонореї":
    st.title("📊 Аналіз кількості захворілих на гонорею")
    st.caption("Графік кількості людей із підтвердженими випадками за часом")
    
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
            data_out = load_and_prepare_data('final_data.csv')
            X_train, y_train, X_test, y_test = data_out
            last_act_date = df['month_dt'].iloc[-1]

            history_df = df.sort_values('month_dt').copy()
            history_df['lag_1'] = history_df['case_count'].shift(1)
            history_df = history_df.dropna()
            history_dates = history_df['month_dt'].tolist()
            X_history = history_df[['lag_1']]
            
            models = get_all_models()
            for name in selected_model_names:
                model = models[name]
                model.fit(X_train, y_train)
                
                # Історія
                hist_preds = model.predict(X_history)
                for d, p in zip(history_dates, hist_preds):
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
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", y=1.1),
            xaxis_title="Дата",
            yaxis_title="Кількість людей"
        )
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# СТОРІНКА 2: СЕЗОННА ДЕКОМПОЗИЦІЯ
# ==========================================
elif page == "📊 Сезонна декомпозиція":
    st.title("📊 Сезонна декомпозиція часового ряду")
    st.caption("Розкладання часового ряду на компоненти: тренд, сезонність та залишки")
    
    try:
        # Підготовка даних
        df_decomp = df[['month_dt', 'case_count']].sort_values('month_dt')
        df_decomp = df_decomp.set_index('month_dt')
        series = df_decomp['case_count'].astype(float)
        
        st.sidebar.header("Налаштування декомпозиції")
        period = st.sidebar.slider("Період сезонності (місяців):", min_value=3, max_value=24, value=12, step=1)
        model_type = st.sidebar.selectbox("Тип декомпозиції:", ["additive", "multiplicative"], index=0)
        
        # Виконання декомпозиції
        with st.spinner("⏳ Виконання сезонної декомпозиції..."):
            result = seasonal_decompose(series, model=model_type, period=period, extrapolate_trend='freq')
        
        # Побудова графіків за допомогою matplotlib
        fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
        fig.suptitle(f'Сезонна декомпозиція ({model_type})', fontsize=14, fontweight='bold')
        
        # Observed
        result.observed.plot(ax=axes[0], color='black', linewidth=1.5)
        axes[0].set_ylabel('Спостережено', fontsize=10)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_title('Фактичні дані', fontsize=11)
        
        # Trend
        result.trend.plot(ax=axes[1], color='blue', linewidth=1.5)
        axes[1].set_ylabel('Тренд', fontsize=10)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_title('Тренд (довгострокова динаміка)', fontsize=11)
        
        # Seasonal
        result.seasonal.plot(ax=axes[2], color='green', linewidth=1.5)
        axes[2].set_ylabel('Сезонність', fontsize=10)
        axes[2].grid(True, alpha=0.3)
        axes[2].set_title('Сезонна компонента', fontsize=11)
        
        # Residuals
        axes[3].plot(result.resid.index, result.resid.values, marker='o', color='red', 
                     linewidth=1, markersize=4, alpha=0.7)
        axes[3].axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        axes[3].set_ylabel('Залишки', fontsize=10)
        axes[3].set_xlabel('Дата', fontsize=10)
        axes[3].grid(True, alpha=0.3)
        axes[3].set_title('Залишки (помилки моделі)', fontsize=11)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Збереження графіку
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "seasonal_decomposition_streamlit.png")
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        st.success(f"✓ Графік збережено: `{output_path}`")
        
        # Статистика
        st.subheader("📈 Статистика компонент")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Середнє значення (спостережено)", f"{result.observed.mean():.2f}")
        
        with col2:
            st.metric("Тренд (початок)", f"{result.trend.iloc[0]:.2f}")
        
        with col3:
            st.metric("Тренд (кінець)", f"{result.trend.iloc[-1]:.2f}")
        
        with col4:
            st.metric("Амплітуда сезонності", f"{result.seasonal.max() - result.seasonal.min():.2f}")
        
        # Додаткові метрики
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric("Стд. відхилення залишків", f"{result.resid.std():.2f}")
        
        with col6:
            st.metric("Кількість спостережень", len(series))
        
        with col7:
            st.metric("Період сезонності", f"{period} міс.")
        
        # Таблиця з компонентами
        st.subheader("📊 Таблиця компонент")
        decomp_table = pd.DataFrame({
            'Дата': result.observed.index,
            'Спостережено': result.observed.values,
            'Тренд': result.trend.values,
            'Сезонність': result.seasonal.values,
            'Залишки': result.resid.values
        })
        st.dataframe(decomp_table.tail(20), use_container_width=True)
        
        st.info("💡 **Інтерпретація**: Тренд показує загальний напрямок захворюваності. Сезонність відображає періодичні коливання. Залишки - це похибки моделі.")
        
    except Exception as e:
        st.error(f"❌ Помилка при виконанні декомпозиції: {e}")

# ==========================================
# СТОРІНКА 3: АНАЛІЗ КОРЕЛЯЦІЇ
# ==========================================
elif page == "📊 Аналіз кореляції":
    st.title("📊 Аналіз кореляції часового ряду")
    st.caption("Матриця кореляції цільової змінної та лагових ознак")
    
    try:
        # Підготовка даних
        df_corr = df[['month_dt', 'case_count']].copy().sort_values('month_dt')
        
        # Створення лагових ознак
        df_corr['lag_1'] = df_corr['case_count'].shift(1)
        df_corr['lag_2'] = df_corr['case_count'].shift(2)
        df_corr['lag_3'] = df_corr['case_count'].shift(3)
        df_corr['lag_12'] = df_corr['case_count'].shift(12)
        
        # Видалення NaN значень
        df_corr_clean = df_corr.dropna()
        
        st.sidebar.header("Налаштування аналізу")
        show_heatmap = st.sidebar.checkbox("Показати теплову карту", value=True)
        show_stats = st.sidebar.checkbox("Показати статистику", value=True)
        show_table = st.sidebar.checkbox("Показати таблицю кореляцій", value=True)
        
        # Розрахунок матриці кореляції
        correlation_matrix = df_corr_clean[['case_count', 'lag_1', 'lag_2', 'lag_3', 'lag_12']].corr()
        
        if show_heatmap:
            st.subheader("🔥 Матриця кореляції")
            
            # Побудова теплової карти
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(
                correlation_matrix, 
                annot=True, 
                cmap='coolwarm', 
                fmt=".4f", 
                square=True, 
                linewidths=1.5,
                cbar_kws={'label': 'Коефіцієнт кореляції'},
                vmin=-1, 
                vmax=1,
                center=0,
                annot_kws={'size': 11, 'weight': 'bold'},
                ax=ax
            )
            
            ax.set_title('Матриця кореляції цільової змінної та лагових ознак', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Ознаки', fontsize=12)
            ax.set_ylabel('Ознаки', fontsize=12)
            
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Збереження графіку
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "correlation_heatmap_streamlit.png")
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            st.success(f"✓ Графік кореляції збережено: `{output_path}`")
        
        if show_stats:
            st.subheader("📈 Статистика кореляцій")
            
            correlations = correlation_matrix['case_count'].sort_values(ascending=False)
            
            # Інтерпретація кореляцій
            stats_data = []
            for feature, corr_val in correlations.items():
                if feature != 'case_count':
                    if corr_val > 0.8:
                        interpretation = "🟢 Дуже сильна позитивна"
                    elif corr_val > 0.6:
                        interpretation = "🟢 Сильна позитивна"
                    elif corr_val > 0.4:
                        interpretation = "🟡 Помірна позитивна"
                    elif corr_val > 0.2:
                        interpretation = "🟡 Слабка позитивна"
                    else:
                        interpretation = "🔴 Дуже слабка/негативна"
                    
                    stats_data.append({
                        'Ознака': feature,
                        'Коефіцієнт кореляції': f"{corr_val:.4f}",
                        'Інтерпретація': interpretation
                    })
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Ключові висновки
            st.info("""
            **📌 Ключові висновки:**
            - **lag_3** (3 місяці тому) має найсильнішу кореляцію - захворюваність повторюється з 3-місячним затримуванням
            - **lag_12** (рік тому) показує сезонність - річна периодичність захворюваності
            - **lag_1** та **lag_2** мають помірну кореляцію - близькі місяці впливають на поточне значення
            """)
        
        if show_table:
            st.subheader("📊 Таблиця кореляцій")
            st.dataframe(correlation_matrix, use_container_width=True)
            
            # Експорт в CSV
            csv_data = correlation_matrix.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Завантажити матрицю кореляції (CSV)",
                data=csv_data,
                file_name="correlation_matrix.csv",
                mime="text/csv"
            )
        
        # Таблиця часового ряду з лагами
        st.subheader("📋 Таблиця часового ряду зі створеними лагами")
        display_table = df_corr_clean[['month_dt', 'case_count', 'lag_1', 'lag_2', 'lag_3', 'lag_12']].copy()
        display_table.columns = ['Дата', 'case_count', 'lag_1', 'lag_2', 'lag_3', 'lag_12']
        st.dataframe(display_table.tail(20), use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Помилка при виконанні аналізу кореляції: {e}")

# ==========================================
# СТОРІНКА 4: МЕТРИКИ
# ==========================================
elif page == "📈 Метрики моделей":
    st.title("📈 Математична оцінка моделей")
    st.write("Розрахунок MAPE, MAE, MSE та RMSE на основі порівняння реальних даних із прогнозами моделей.")
    
    try:
        data_out = load_and_prepare_data('final_data.csv')
        X_train, y_train, X_eval, y_eval = data_out
        
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
