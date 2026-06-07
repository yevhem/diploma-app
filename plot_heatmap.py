import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Вкажіть тут свої "сміттєві" колонки, які потрібно видалити перед аналізом
GARBAGE_COLS = ['date', 'city_name', 'id_patient']

data_path = Path('final_data.csv')
if not data_path.exists():
    raise FileNotFoundError('final_data.csv not found. Please provide the dataset in the repository root.')

df = pd.read_csv(data_path)

# Видаляємо вказані сміттєві колонки, якщо вони є
cols_to_drop = [c for c in GARBAGE_COLS if c in df.columns]
if cols_to_drop:
    df = df.drop(columns=cols_to_drop)

# Залишаємо тільки числові колонки
df_num = df.select_dtypes(include=[np.number])
if df_num.shape[1] == 0:
    raise ValueError('No numeric columns found in final_data.csv to compute correlation.')

# Обчислюємо матрицю кореляції
corr = df_num.corr()

# Фільтруємо колонки: залишаємо ті, у яких є хоча б одна кореляція за модулем >= 0.95
strong_cols = [col for col in corr.columns if corr[col].abs().drop(col).max() >= 0.95]
if not strong_cols:
    raise ValueError('No columns with correlation >= 0.95 found. No heatmap generated.')

filtered_corr = corr.loc[strong_cols, strong_cols]

plt.figure(figsize=(10, 8))
sns.heatmap(filtered_corr, annot=True, cmap='coolwarm', fmt='.2f', square=True, cbar_kws={'shrink': 0.8})
plt.title('Correlation heatmap (|corr| >= 0.95)')
plt.tight_layout()

out_dir = Path('outputs')
out_dir.mkdir(exist_ok=True)
out = out_dir / 'correlation_heatmap.png'
plt.savefig(out, dpi=300)
print(f'Heatmap saved: {out.resolve()}')
