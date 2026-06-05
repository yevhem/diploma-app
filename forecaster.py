import numpy as np
from typing import List
from sklearn.base import RegressorMixin

def predict_future(model: RegressorMixin, last_value: float, months_to_predict: int) -> List[float]:
    """
    Führt eine rekursive Vorhersage für zukünftige Monate durch.
    (Виконує рекурсивний прогноз на майбутні місяці.)
    
    Args:
        model: Das trainierte ML-Modell. (Навчена ML-модель)
        last_value: Der letzte bekannte Wert. (Останнє відоме значення)
        months_to_predict: Anzahl der Monate für die Vorhersage. (Кількість місяців для прогнозу)
        
    Returns:
        List[float]: Eine Liste mit den vorhergesagten Werten. (Список прогнозованих значень)
    """
    forecast = []
    current_input = np.array([[last_value]])
    
    for _ in range(months_to_predict):
        # Vorhersage des nächsten Wertes
        pred = float(model.predict(current_input)[0])
        forecast.append(pred)
        
        # Aktualisierung des Inputs für den nächsten Schritt (rekursive Anwendung)
        # Оновлення вхідних даних для наступного кроку (рекурсивне застосування)
        current_input = np.array([[pred]]) 
        
    return forecast