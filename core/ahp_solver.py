import numpy as np
from core.models import MatrixModel

def calculate_ahp_weights(matrix_data: list[list[float]]) -> dict:
    """Расчет весов критериев/альтернатив методом АИИ"""
    model = MatrixModel(matrix=matrix_data)
    matrix = np.array(model.matrix)
    
    # 1. Нормализация столбцов
    col_sums = matrix.sum(axis=0)
    normalized = matrix / col_sums
    
    # 2. Вычисление весов (среднее по строкам)
    weights = normalized.mean(axis=1)
    
    # 3. Проверка согласованности
    lambda_max = (matrix @ weights) / weights
    lambda_max = np.mean(lambda_max)
    
    n = matrix.shape[0]
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0
    
    # Полная таблица RI по Саати
    ri_table = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
    }
    ri = ri_table.get(n, 1.49)  # Для n>10 используем 1.49
    cr = ci / ri if ri > 0 else 0
    
    return {
        "weights": weights.tolist(),
        "consistency_ratio": float(cr),
        "is_consistent": cr < 0.1
    }