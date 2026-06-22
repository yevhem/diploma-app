import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from statsmodels.tsa.seasonal import seasonal_decompose


def ensure_output_dir():
    out_dir = Path('outputs')
    out_dir.mkdir(exist_ok=True)
    return out_dir


def prepare_lag_features(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df['month'] = pd.to_datetime(df['month'])
    df = df.sort_values('month')
    for lag in [1, 2, 3, 12]:
        df[f'lag_{lag}'] = df['case_count'].shift(lag)
    df = df.dropna().reset_index(drop=True)
    return df


def plot_feature_importance(out_dir: Path, df: pd.DataFrame) -> None:
    features = ['lag_3', 'lag_12', 'lag_1', 'lag_2']
    X = df[features]
    y = df['case_count']

    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)

    xgb = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    rf = RandomForestRegressor(n_estimators=100, random_state=42)

    xgb.fit(train_X, train_y)
    rf.fit(train_X, train_y)

    xgb_importances = xgb.feature_importances_
    rf_importances = rf.feature_importances_

    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharex=False)
    axes[0].barh(features[::-1], xgb_importances[::-1], color='#117A65')
    axes[0].set_title('Feature importance in XGBoost model', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Relative importance (Gain)', fontsize=12)
    axes[0].set_ylabel('Features', fontsize=12)
    axes[0].grid(axis='x', alpha=0.3)

    axes[1].barh(features[::-1], rf_importances[::-1], color='#E67E22')
    axes[1].set_title('Feature importance in Random Forest model', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Relative importance (Gini Importance)', fontsize=12)
    axes[1].set_ylabel('')
    axes[1].grid(axis='x', alpha=0.3)

    plt.tight_layout()
    output_path = out_dir / 'feature_importance_comparison_en.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ Saved {output_path}')


def plot_hyperparameter_tuning(out_dir: Path, df: pd.DataFrame) -> None:
    features = ['lag_1', 'lag_2', 'lag_3', 'lag_12']
    X = df[features]
    y = df['case_count']

    train_X, val_X, train_y, val_y = train_test_split(X, y, test_size=0.2, random_state=42)
    n_estimators = list(range(10, 201, 10))
    train_mae = []
    val_mae = []

    for n in n_estimators:
        model = XGBRegressor(n_estimators=n, random_state=42, verbosity=0)
        model.fit(train_X, train_y)
        train_preds = model.predict(train_X)
        val_preds = model.predict(val_X)
        train_mae.append(mean_absolute_error(train_y, train_preds))
        val_mae.append(mean_absolute_error(val_y, val_preds))

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(n_estimators, train_mae, marker='o', color='#2E86AB', label='Train MAE')
    ax.plot(n_estimators, val_mae, marker='s', color='#C0392B', label='Validation MAE')
    ax.set_title('Hyperparameter tuning curves for n_estimators in XGBoost model', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of base trees (n_estimators)', fontsize=12)
    ax.set_ylabel('Mean absolute error (MAE)', fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = out_dir / 'hyperparameter_tuning_curves_en.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ Saved {output_path}')


def plot_residuals(out_dir: Path, df: pd.DataFrame) -> None:
    features = ['lag_1', 'lag_2', 'lag_3', 'lag_12']
    X = df[features]
    y = df['case_count']

    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    model.fit(train_X, train_y)
    preds = model.predict(test_X)
    residuals = test_y.values - preds

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.scatter(preds, residuals, color='#8E44AD', edgecolor='black', s=70, alpha=0.85)
    ax.axhline(0, color='red', linestyle='--', linewidth=1.25, alpha=0.7)
    ax.set_title('Residuals plot for XGBoost model', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted values', fontsize=12)
    ax.set_ylabel('Residuals (Actual - Predicted)', fontsize=12)
    ax.legend(['Zero error line', 'Model residuals'], fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = out_dir / 'residuals_plot_en.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ Saved {output_path}')


def plot_decomposition(out_dir: Path, df: pd.DataFrame) -> None:
    df = df.copy()
    df['month'] = pd.to_datetime(df['month'])
    df = df.sort_values('month').set_index('month')
    series = df['case_count'].astype(float)
    result = seasonal_decompose(series, model='additive', period=12, extrapolate_trend='freq')

    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    result.observed.plot(ax=axes[0], color='black', linewidth=1.5)
    axes[0].set_ylabel('Observed', fontsize=10)
    axes[0].set_title('Observed data', fontsize=11)
    axes[0].grid(True, alpha=0.3)

    result.trend.plot(ax=axes[1], color='blue', linewidth=1.5)
    axes[1].set_ylabel('Trend', fontsize=10)
    axes[1].set_title('Trend (long-term dynamics)', fontsize=11)
    axes[1].grid(True, alpha=0.3)

    result.seasonal.plot(ax=axes[2], color='green', linewidth=1.5)
    axes[2].set_ylabel('Seasonal', fontsize=10)
    axes[2].set_title('Seasonal component', fontsize=11)
    axes[2].grid(True, alpha=0.3)

    axes[3].plot(result.resid.index, result.resid.values, marker='o', color='red', linewidth=1, markersize=4, alpha=0.7)
    axes[3].axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    axes[3].set_ylabel('Residuals', fontsize=10)
    axes[3].set_xlabel('Date', fontsize=10)
    axes[3].set_title('Residuals (model errors)', fontsize=11)
    axes[3].grid(True, alpha=0.3)

    fig.suptitle('Seasonal decomposition of gonorrhea morbidity time series', fontsize=14, fontweight='bold')
    plt.tight_layout()
    output_path = out_dir / 'decomposition_en.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ Saved {output_path}')


def main():
    out_dir = ensure_output_dir()
    df = prepare_lag_features('final_data.csv')
    plot_feature_importance(out_dir, df)
    plot_hyperparameter_tuning(out_dir, df)
    plot_residuals(out_dir, df)
    plot_decomposition(out_dir, pd.read_csv('final_data.csv'))


if __name__ == '__main__':
    main()
