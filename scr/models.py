from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import PoissonRegressor
from xgboost import XGBRegressor

def get_all_models():
    return {
        "Poisson Regression": PoissonRegressor(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42)
    }