import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Вкажіть тут свої "сміттєві" колонки, які потрібно видалити перед аналізом
GARBAGE_COLS = ['date', 'city_name', 'id_patient']
THRESHOLD = 0.95

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

# Шукаємо пари колонок з |corr| >= THRESHOLD (без діагоналі)
corr_abs = corr.abs()
pairs = []
cols_in_pairs = set()
for i in range(len(corr.columns)):
    for j in range(i + 1, len(corr.columns)):
        if corr_abs.iat[i, j] >= THRESHOLD:
            a = corr.columns[i]
            b = corr.columns[j]
            pairs.append((a, b, corr.iat[i, j]))
            cols_in_pairs.update([a, b])

plt.figure(figsize=(10, 8))
if len(cols_in_pairs) >= 2:
    filtered_corr = corr.loc[sorted(cols_in_pairs), sorted(cols_in_pairs)]
    sns.heatmap(filtered_corr, annot=True, cmap='coolwarm', fmt='.2f', square=True, cbar_kws={'shrink': 0.8})
    plt.title(f'Correlation heatmap (pairs with |corr| >= {THRESHOLD})')
else:
    # Якщо сильних пар немає або тільки одна колонка — показуємо повну матрицю,
    # але замаскуємо значення з модулем меншим за поріг і не підписуватимемо їх.
    mask = corr_abs < THRESHOLD
    annot = corr.round(2).astype(str)
    annot = annot.where(~mask, other='')
    sns.heatmap(corr, annot=annot, cmap='coolwarm', fmt='', square=True, cbar_kws={'shrink': 0.8}, mask=mask)
    plt.title(f'Correlation heatmap (values with |corr| < {THRESHOLD} hidden)')
plt.tight_layout()

out_dir = Path('outputs')
out_dir.mkdir(exist_ok=True)
out = out_dir / 'correlation_heatmap.png'
plt.savefig(out, dpi=300)
print(f'Heatmap saved: {out.resolve()}')
