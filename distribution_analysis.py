import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Завантаження даних
df = pd.read_csv('final_data.csv')
print("=" * 60)
print("АНАЛІЗ РОЗПОДІЛУ ЗАХВОРЮВАНОСТІ")
print("=" * 60)
print(f"Завантажено: {len(df)} спостережень\n")

# Статистика розподілу
print("ОПИСОВА СТАТИСТИКА:")
print("=" * 60)
print(f"Середнє значення:        {df['case_count'].mean():.2f}")
print(f"Медіана:                 {df['case_count'].median():.2f}")
print(f"Мода:                    {df['case_count'].mode().values[0]:.2f}")
print(f"Стандартне відхилення:   {df['case_count'].std():.2f}")
print(f"Дисперсія:               {df['case_count'].var():.2f}")
print(f"Мінімум:                 {df['case_count'].min():.2f}")
print(f"Максимум:                {df['case_count'].max():.2f}")
print(f"Q1 (25%):                {df['case_count'].quantile(0.25):.2f}")
print(f"Q3 (75%):                {df['case_count'].quantile(0.75):.2f}")
iqr = df['case_count'].quantile(0.75) - df['case_count'].quantile(0.25)
print(f"IQR (міжквартильний розмах): {iqr:.2f}")
print("=" * 60)

# Детекція викидів за методом IQR
Q1 = df['case_count'].quantile(0.25)
Q3 = df['case_count'].quantile(0.75)
lower_bound = Q1 - 1.5 * iqr
upper_bound = Q3 + 1.5 * iqr
outliers = df[(df['case_count'] < lower_bound) | (df['case_count'] > upper_bound)]

print(f"\nДЕТЕКЦІЯ ВИКИДІВ (метод IQR):")
print(f"Нижня межа: {lower_bound:.2f}")
print(f"Верхня межа: {upper_bound:.2f}")
print(f"Кількість викидів: {len(outliers)}")
if len(outliers) > 0:
    print("Викиди:")
    for idx, row in outliers.iterrows():
        print(f"  - {row['month']}: {row['case_count']} випадків")

# Побудова графіків
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Лівий графік — гістограма з кривою щільності
sns.histplot(df['case_count'], kde=True, ax=axes[0], color='teal', bins=20, edgecolor='black')
axes[0].set_title('Гістограма розподілу частот захворюваності', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Кількість зареєстрованих випадків', fontsize=11)
axes[0].set_ylabel('Частота (кількість місяців)', fontsize=11)
axes[0].grid(True, alpha=0.3)
axes[0].axvline(df['case_count'].mean(), color='red', linestyle='--', linewidth=2, label=f'Середнє: {df["case_count"].mean():.1f}')
axes[0].axvline(df['case_count'].median(), color='green', linestyle='--', linewidth=2, label=f'Медіана: {df["case_count"].median():.1f}')
axes[0].legend()

# Правий графік — Boxplot для детекції викидів
bp = sns.boxplot(y=df['case_count'], ax=axes[1], color='orange')
axes[1].set_title('Діаграма розмаху (Boxplot) для детекції викидів', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Кількість зареєстрованих випадків', fontsize=11)
axes[1].grid(True, alpha=0.3, axis='y')

# Додаємо значення на boxplot
median = df['case_count'].median()
q1 = df['case_count'].quantile(0.25)
q3 = df['case_count'].quantile(0.75)
axes[1].text(0.15, median, f'Медіана\n{median:.1f}', fontsize=9, ha='left')
axes[1].text(0.15, q1, f'Q1\n{q1:.1f}', fontsize=9, ha='left')
axes[1].text(0.15, q3, f'Q3\n{q3:.1f}', fontsize=9, ha='left')

plt.suptitle('Аналіз розподілу захворюваності на гонорею', fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()

# Збереження
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)
output_path = output_dir / 'distribution_analysis.png'

fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f'\n✓ Графік розподілу збережено: {output_path.resolve()}')

plt.show()
