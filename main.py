import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.data_prep import load_and_prepare_data
from src.models import get_all_models

def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def plot_and_save(y_true, y_pred, model_name):
    # Визначаємо повний шлях
    filename = f"{model_name}_plot.png"
    filepath = os.path.join(os.getcwd(), filename)
    
    plt.figure(figsize=(10, 5))
    plt.plot(y_true.values, label='Реальні дані', marker='o')
    plt.plot(y_pred, label='Прогноз', marker='x')
    plt.title(f'Порівняння: {model_name}')
    plt.legend()
    plt.savefig(filename)
    plt.close()
    
    print(f">>> ФАЙЛ ЗБЕРЕЖЕНО ТУТ: {filepath}")

# 1. Завантаження
X_train, y_train, X_test, y_test = load_and_prepare_data('data/final_data.csv')

# 2. Навчання та оцінка
models = get_all_models()

print("--- ЗВІТ ---")

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    # Розрахунок метрик
    mae = mean_absolute_error(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    rmse = np.sqrt(mse)
    mape = mean_absolute_percentage_error(y_test.values, preds)
    
    print(f"\nМодель: {name}")
    print(f"MAE: {mae:.2f}")
    
    # Малювання графіка
    plot_and_save(y_test, preds, name)