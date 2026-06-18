import pytest
import numpy as np
from core.game_solver import find_nash_equilibrium

def test_nash_prisoners_dilemma():
    """Классическая дилемма заключенного (упрощенная)"""
    # Стратегии: Молчать, Предать
    matrix = [[3, 0], [5, 1]] 
    res = find_nash_equilibrium(matrix)
    assert res['equilibria_found'] >= 1
    # В дилемме заключенного равновесие в чистых стратегиях (Предать, Предать)
    assert np.allclose(res['strategies'][0]['player_1_strategy'], [0, 1])

def test_nash_matching_pennies():
    """Игра с нулевой суммой без равновесия в чистых стратегиях"""
    matrix = [[1, -1], [-1, 1]]
    res = find_nash_equilibrium(matrix)
    assert res['equilibria_found'] == 1
    # Смешанная стратегия 50/50
    assert np.allclose(res['strategies'][0]['player_1_strategy'], [0.5, 0.5])