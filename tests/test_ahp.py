import pytest
import numpy as np
from core.ahp_solver import calculate_ahp_weights

def test_ahp_identity_matrix():
    """Если все элементы равны 1, веса должны быть одинаковыми"""
    matrix = [[1, 1], [1, 1]]
    res = calculate_ahp_weights(matrix)
    assert np.allclose(res['weights'], [0.5, 0.5])
    assert res['consistency_ratio'] == 0.0

def test_ahp_inconsistent_matrix():
    """Проверка матрицы с нарушением транзитивности"""
    matrix = [[1, 9, 1], [1/9, 1, 9], [1, 1/9, 1]]
    res = calculate_ahp_weights(matrix)
    assert res['is_consistent'] == False

def test_ahp_invalid_matrix():
    """Тест на неквадратную матрицу (должен упасть с ошибкой Pydantic)"""
    matrix = [[1, 2], [3, 4], [5, 6]]
    with pytest.raises(Exception):
        calculate_ahp_weights(matrix)