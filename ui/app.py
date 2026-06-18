import sys
import os

# Добавляем корневую папку проекта в пути поиска Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from core.ahp_solver import calculate_ahp_weights
from core.game_solver import find_nash_equilibrium

st.set_page_config(page_title="MarketingSelector", layout="wide")
st.title("MarketingSelector: АИИ + Теория Игр")

# --- Кэширование тяжелых расчетов (требование из ТЗ) ---
@st.cache_data
def run_ahp(matrix):
    return calculate_ahp_weights(matrix)

@st.cache_data
def run_game(matrix):
    return find_nash_equilibrium(matrix)

# --- Вкладка 1: АИИ ---
st.header("1. Оценка каналов (АИИ)")
st.markdown("Введите матрицу попарных сравнений каналов (например, SEO, SMM, Ads).")

channels = st.text_input("Названия каналов через запятую", "SEO, SMM, Ads, Email")
n_channels = len(channels.split(','))

# Генерация матрицы в UI
st.subheader("Матрица сравнения")
matrix_ahp = []
cols = st.columns(n_channels)
for i in range(n_channels):
    row = []
    for j in range(n_channels):
        if i == j:
            val = 1.0
        elif j < i:
            val = 1.0 / matrix_ahp[j][i] # Симметрия
        else:
            val = cols[j].number_input(f"Канал {i+1} к Каналу {j+1}", min_value=0.1, max_value=9.0, value=1.0, step=0.1, key=f"ahp_{i}_{j}")
        row.append(val)
    matrix_ahp.append(row)

if st.button("Рассчитать АИИ"):
    try:
        res = run_ahp(matrix_ahp)
        st.success(f"Индекс согласованности (CR): {res['consistency_ratio']:.3f} {'✅' if res['is_consistent'] else '⚠️ (нестабильно)'}")
        
        df = pd.DataFrame({
            "Канал": channels.split(','),
            "Вес (Приоритет)": [f"{w:.3f}" for w in res['weights']]
        })
        st.table(df)
    except Exception as e:
        st.error(f"Ошибка валидации: {e}")

# --- Вкладка 2: Матричная Игра ---
st.header("2. Распределение бюджета (Игра с конкурентом)")
st.markdown("Платежная матрица (выигрыш нашей компании в долях рынка). Строки - наши стратегии, Столбцы - стратегии конкурента.")

rows_game = st.number_input("Кол-во наших стратегий", 2, 5, 2)
cols_game = st.number_input("Кол-во стратегий конкурента", 2, 5, 2)

matrix_game = []
for i in range(rows_game):
    row = []
    for j in range(cols_game):
        val = st.number_input(f"Выигрыш [{i+1},{j+1}]", value=0.0, key=f"game_{i}_{j}")
        row.append(val)
    matrix_game.append(row)

if st.button("Найти Равновесие Нэша"):
    try:
        res = run_game(matrix_game)
        if res['equilibria_found'] > 0:
            st.success(f"Найдено равновесий: {res['equilibria_found']}")
            for idx, eq in enumerate(res['strategies']):
                st.subheader(f"Равновесие #{idx+1}")
                st.write("**Наша оптимальная стратегия (доли бюджета):**", [f"{x:.2f}" for x in eq['player_1_strategy']])
                st.write("**Стратегия конкурента:**", [f"{x:.2f}" for x in eq['player_2_strategy']])
        else:
            st.warning("Равновесие в чистых/смешанных стратегиях не найдено.")
    except Exception as e:
        st.error(f"Ошибка: {e}")