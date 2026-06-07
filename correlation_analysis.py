import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Завантаження даних
df = pd.read_csv('final_data.csv')
df['month'] = pd.to_datetime(df['month'])
df = df.sort_values('month')

print("=" * 60)
print("АНАЛІЗ КОРЕЛЯЦІЇ ЧАСОВОГО РЯДУ ЗАХВОРЮВАНОСТІ")
print("=" * 60)
print(f"Завантажено: {len(df)} спостережень\n")

# Створення лагових ознак
df['lag_1'] = df['case_count'].shift(1)   # Попередній місяць
df['lag_2'] = df['case_count'].shift(2)   # 2 місяці тому
df['lag_3'] = df['case_count'].shift(3)   # 3 місяці тому
df['lag_12'] = df['case_count'].shift(12)  # Рік тому (сезонність)

# Видаляємо NaN значення (виникають через лаги)
df_corr = df[['case_count', 'lag_1', 'lag_2', 'lag_3', 'lag_12']].dropna()

print(f"Дійсні спостереження для аналізу: {len(df_corr)}\n")

# Розрахунок матриці кореляції
correlation_matrix = df_corr.corr()

print("МАТРИЦЯ КОРЕЛЯЦІЇ:")
print("=" * 60)
print(correlation_matrix.to_string())
print("=" * 60)

# Статистика кореляцій
print("\nСТАТИСТИКА КОРЕЛЯЦІЙ ЗІ ЗМІННОЮ 'case_count':")
correlations = correlation_matrix['case_count'].sort_values(ascending=False)
for feature, corr_val in correlations.items():
    if feature != 'case_count':
        print(f"  {feature:12} : {corr_val:7.4f}", end="")
        # Інтерпретація
        if corr_val > 0.8:
            print("  (Дуже сильна позитивна)")
        elif corr_val > 0.6:
            print("  (Сильна позитивна)")
        elif corr_val > 0.4:
            print("  (Помірна позитивна)")
        elif corr_val > 0.2:
            print("  (Слабка позитивна)")
        else:
            print("  (Дуже слабка або негативна)")

# Побудова теплової карти
plt.figure(figsize=(10, 8))
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
    annot_kws={'size': 11, 'weight': 'bold'}
)

plt.title('Матриця кореляції цільової змінної та лагових ознак', 
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Ознаки', fontsize=12)
plt.ylabel('Ознаки', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# Збереження
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)
output_path = output_dir / 'correlation_heatmap.png'

plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Графік кореляції збережено: {output_path.resolve()}")

# Експорт матриці кореляції у CSV
csv_path = output_dir / 'correlation_matrix.csv'
correlation_matrix.to_csv(csv_path)
print(f"✓ Матриця кореляції збережена у CSV: {csv_path.resolve()}\n")

plt.show()
