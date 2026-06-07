import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Відформатовано згідно вашого прикладу: вивід head, вибір числових колонок, повна матриця
data_path = Path('final_data.csv')
if not data_path.exists():
    raise FileNotFoundError('final_data.csv not found. Please provide the dataset in the repository root.')

df = pd.read_csv(data_path)

# Видаляємо можливі "сміттєві" колонки
GARBAGE_COLS = ['date', 'city_name', 'id_patient']
cols_to_drop = [c for c in GARBAGE_COLS if c in df.columns]
if cols_to_drop:
    df = df.drop(columns=cols_to_drop)

# 1. Переконаємося, що df містить дані
print('Перші 5 рядків датасету:')
print(df.head().to_string())

# 2. Вибираємо тільки числові колонки
numeric_df = df.select_dtypes(include=['float64', 'int64'])

# 3. Перевірка колонок
print('Колонки, які будуть на графіку:', list(numeric_df.columns))

# 4. Матриця кореляції для всіх числових колонок
correlation_matrix = numeric_df.corr()

# 5. Малюємо та зберігаємо повну матрицю
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Матриця кореляції')
plt.tight_layout()

out_dir = Path('outputs')
out_dir.mkdir(exist_ok=True)
out_full = out_dir / 'correlation_heatmap_full.png'
plt.savefig(out_full, dpi=300)
print(f'Full heatmap saved: {out_full.resolve()}')
