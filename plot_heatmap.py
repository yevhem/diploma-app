import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

data_path = Path('final_data.csv')
if not data_path.exists():
    raise FileNotFoundError('final_data.csv not found. Please provide the dataset in the repository root.')

df = pd.read_csv(data_path)
df_num = df.select_dtypes(include=[np.number])
if df_num.shape[1] == 0:
    raise ValueError('No numeric columns found in final_data.csv to compute correlation.')

corr = df_num.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', square=True, cbar_kws={'shrink': 0.8})
plt.title('Correlation heatmap')
plt.tight_layout()
out = Path('correlation_heatmap.png')
plt.savefig(out, dpi=300)
print(f'Heatmap saved: {out.resolve()}')
