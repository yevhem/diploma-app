import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from statsmodels.tsa.seasonal import seasonal_decompose
import os

# Завантаження даних
data_path = Path('final_data.csv')
if not data_path.exists():
    raise FileNotFoundError('final_data.csv not found. Place your dataset in repository root.')

df = pd.read_csv(data_path)
print(f"Завантажено дані: {len(df)} записів")
print(f"Колонки: {df.columns.tolist()}")

# Підготовка даних
df['month'] = pd.to_datetime(df['month'])
df = df.sort_values('month')
df = df.set_index('month')

if 'case_count' not in df.columns:
    raise KeyError('No "case_count" column found in the dataset.')

series = df['case_count'].astype(float)
print(f"Часовий ряд: {len(series)} спостережень")
print(f"Період: {series.index[0].date()} до {series.index[-1].date()}")

# Сезонна декомпозиція (period=12 для щомісячних даних з річною сезонністю)
print("\nВиконання сезонної декомпозиції...")
result = seasonal_decompose(series, model='additive', period=12, extrapolate_trend='freq')

# Побудова графіків
fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
fig.suptitle('Сезонна декомпозиція часового ряду захворюваності на гонорею', 
             fontsize=14, fontweight='bold', y=0.995)

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
axes[3].set_title('Залишки (помилки)', fontsize=11)

plt.tight_layout()

# Збереження результату
out_dir = Path('outputs')
out_dir.mkdir(exist_ok=True)
out_path = out_dir / 'seasonal_decomposition.png'

fig.savefig(out_path, dpi=300, bbox_inches='tight')
print(f'\n✓ Графік декомпозиції збережено: {out_path.resolve()}')

# Збереження англомовної копії
axes[0].set_ylabel('Observed', fontsize=10)
axes[0].set_title('Observed data', fontsize=11)
axes[1].set_ylabel('Trend', fontsize=10)
axes[1].set_title('Trend (long-term dynamics)', fontsize=11)
axes[2].set_ylabel('Seasonal', fontsize=10)
axes[2].set_title('Seasonal component', fontsize=11)
axes[3].set_ylabel('Residuals', fontsize=10)
axes[3].set_xlabel('Date', fontsize=10)
axes[3].set_title('Residuals (model errors)', fontsize=11)
fig.suptitle('Seasonal decomposition of gonorrhea morbidity time series', fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
out_path_en = out_dir / 'seasonal_decomposition_en.png'
fig.savefig(out_path_en, dpi=300, bbox_inches='tight')
print(f'✓ English chart saved: {out_path_en.resolve()}')

# Виведення статистики
print(f"\n--- Статистика компонент ---")
print(f"Середнє значення спостережуваних: {result.observed.mean():.2f}")
print(f"Тренд (початок): {result.trend.iloc[0]:.2f}")
print(f"Тренд (кінець): {result.trend.iloc[-1]:.2f}")
print(f"Амплітуда сезонності: {result.seasonal.max() - result.seasonal.min():.2f}")
print(f"Стандартне відхилення залишків: {result.resid.std():.2f}")

plt.show()
