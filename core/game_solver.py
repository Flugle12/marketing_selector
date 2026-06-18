import nashpy as nash
import numpy as np
from pydantic import BaseModel, field_validator

class GameMatrixModel(BaseModel):
    matrix: list[list[float]]

    @field_validator('matrix')
    @classmethod
    def check_2d(cls, v):
        arr = np.array(v)
        if arr.ndim != 2:
            raise ValueError("Матрица должна быть двумерной")
        return v

def find_nash_equilibrium(payoff_matrix: list[list[float]]) -> dict:
    """Поиск равновесия Нэша в смешанных стратегиях"""
    model = GameMatrixModel(matrix=payoff_matrix)
    matrix = np.array(model.matrix)
    
    # Создаем игру (для игрока 1 матрица, для игрока 2 - транспонированная с минусом, 
    # если игра с нулевой суммой. Здесь считаем матрицу выигрышей Игрока 1)
    game = nash.Game(matrix)
    
    # Ищем равновесия
    equilibria = list(game.support_enumeration())
    
    results = []
    for eq in equilibria:
        results.append({
            "player_1_strategy": eq[0].tolist(), # Наши доли бюджета
            "player_2_strategy": eq[1].tolist()  # Доли конкурента
        })
        
    return {
        "equilibria_found": len(results),
        "strategies": results
    }