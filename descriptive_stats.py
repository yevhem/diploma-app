import pandas as pd
from pathlib import Path

# Попробовать загрузить final_data.csv; измените путь при необходимости
data_path = Path('final_data.csv')
if data_path.exists():
    df = pd.read_csv(data_path)
else:
    # Если ваш файл имеет другое имя — раскомментируйте и укажите путь
    # df = pd.read_csv('your_file.csv')
    raise FileNotFoundError("final_data.csv not found. Please update descriptive_stats.py to load your file.")

# Получение описательной статистики
stats = df.describe()

# Сохранение в файл, который затем можно скопировать в Word
stats.to_csv('descriptive_stats.csv')
print("Таблица сохранена в файл descriptive_stats.csv")
