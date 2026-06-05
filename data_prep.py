import pandas as pd
import logging

# Налаштування логування, щоб бачити помилки в терміналі
logging.basicConfig(level=logging.INFO)

def load_and_prepare_data(filepath: str, split_ratio: float = 0.8):
    """
    Завантажує дані з CSV, виконує базову обробку та розділяє на вибірки.
    
    Args:
        filepath (str): Шлях до файлу.
        split_ratio (float): Відсоток даних для навчання (за замовчуванням 0.8).
        
    Returns:
        tuple: (X_train, y_train, X_test, y_test)
    """
    try:
        df = pd.read_csv(filepath)
        
        # Перевірка наявності необхідних колонок
        required_cols = ['month', 'case_count']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Файл має містити колонки: {required_cols}")

        df['month'] = pd.to_datetime(df['month'])
        df = df.sort_values('month')
        
        # Створення лагових ознак (lag feature) для прогнозування
        df['lag_1'] = df['case_count'].shift(1)
        df = df.dropna()
        
        # Розрахунок точки розділення
        split_point = int(len(df) * split_ratio)
        
        train = df.iloc[:split_point]
        test = df.iloc[split_point:]
        
        logging.info("Дані успішно підготовлені.")
        return train[['lag_1']], train['case_count'], test[['lag_1']], test['case_count']

    except Exception as e:
        logging.error(f"Помилка при підготовці даних: {e}")
        raise