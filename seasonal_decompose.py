import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from statsmodels.tsa.seasonal import seasonal_decompose

data_path = Path('final_data.csv')
if not data_path.exists():
    raise FileNotFoundError('final_data.csv not found. Place your dataset in repository root.')

df = pd.read_csv(data_path)

# Якщо є колонка з датами — спробуємо її використати
date_col = None
for candidate in ['date', 'month', 'ds']:
    if candidate in df.columns:
        date_col = candidate
        break

if date_col:
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
else:
    # Якщо індексу немає — створимо його як місячний
    df.index = pd.date_range(start='2020-01-01', periods=len(df), freq='M')

if 'case_count' not in df.columns and 'case_count' not in df.index:
    raise KeyError('No "case_count" column found in the dataset.')

series = df['case_count'].astype(float)

# Декомпозиція (period=12 для щорічної сезонності)
result = seasonal_decompose(series, model='additive', period=12, extrapolate_trend='freq')

fig = result.plot()
fig.set_size_inches(10, 8)

out_dir = Path('outputs')
out_dir.mkdir(exist_ok=True)
out_path = out_dir / 'decomposition.png'
fig.savefig(out_path, dpi=200)
print(f'Decomposition plot saved: {out_path.resolve()}')
