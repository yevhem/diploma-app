import pandas as pd
from pathlib import Path

# Попробовать загрузити final_data.csv; змініть шлях при необхідності
data_path = Path('final_data.csv')
if data_path.exists():
    df = pd.read_csv(data_path)
else:
    # Якщо ваш файл має іншу назву — розкоментуйте і вкажіть свій шлях
    # df = pd.read_csv('your_file.csv')
    raise FileNotFoundError("final_data.csv not found. Please update descriptive_stats.py to load your file.")

# Отримання описової статистики
stats = df.describe()

# Папка для збереження результатів
out_dir = Path('outputs')
out_dir.mkdir(exist_ok=True)

# Збереження у файл в папці outputs
out_path = out_dir / 'descriptive_stats.csv'
stats.to_csv(out_path)
print(f"Таблиця збережена у файл {out_path}")
