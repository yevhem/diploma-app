import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Встановлення стилю
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 7)

# Завантаження даних
df = pd.read_csv('final_data.csv')
df['month_dt'] = pd.to_datetime(df['month'])

# Створення фігури
fig, ax = plt.subplots(figsize=(14, 7))

# Побудова основного графіку
ax.plot(df['month_dt'], df['case_count'], 
        marker='o', linewidth=2.5, markersize=6, 
        color='#2E86AB', label='Кількість випадків захворюваності')

# Оформлення
ax.set_xlabel('Дата', fontsize=12, fontweight='bold')
ax.set_ylabel('Кількість випадків', fontsize=12, fontweight='bold')
ax.set_title('Графік захворюваності (2017-2021)', fontsize=14, fontweight='bold', pad=20)

# Додавання сітки
ax.grid(True, alpha=0.3)

# Форматування осі X
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45, ha='right')

# Легенда
ax.legend(loc='upper right', fontsize=11)

# Автоматичне налаштування макета
plt.tight_layout()

# Створення папки outputs, якщо вона не існує
os.makedirs('outputs', exist_ok=True)

# Збереження графіку
output_path = 'outputs/morbidity_chart.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✓ Графік збережено: {output_path}")

plt.show()
