import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from core.ahp_solver import calculate_ahp_weights
from core.game_solver import find_nash_equilibrium
from pathlib import Path
import yaml

st.set_page_config(page_title="MarketingSelector", layout="wide")
st.title("MarketingSelector: АИИ + Теория Игр")


# Кэширование тяжелых расчетов
@st.cache_data
def run_ahp(matrix):
    return calculate_ahp_weights(matrix)


@st.cache_data
def run_game(matrix):
    return find_nash_equilibrium(matrix)


#  Инициализация session_state значениями по умолчанию 
if 'channels_input' not in st.session_state:
    st.session_state['channels_input'] = "SEO, SMM, Ads, Email"
if 'rows_game' not in st.session_state:
    st.session_state['rows_game'] = 2
if 'cols_game' not in st.session_state:
    st.session_state['cols_game'] = 2


#  Sidebar: выбор и загрузка сценария 
st.sidebar.header("Сценарии")

scenario = st.sidebar.selectbox(
    "Выберите сценарий для демонстрации:",
    ["A: Штатный (happy path)",
     "Б: Пограничный (CR на грани)",
     "В: Стрессовый (нарушение)"]
)

scenario_files = {
    "A: Штатный (happy path)": "scenario_a_happy_path.yaml",
    "Б: Пограничный (CR на грани)": "scenario_b_borderline.yaml",
    "В: Стрессовый (нарушение)": "scenario_c_stress.yaml"
}

if st.sidebar.button("Загрузить сценарий"):
    config_path = Path("config") / scenario_files[scenario]

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        st.sidebar.error(f"Ошибка чтения файла: {e}")
        st.stop()

    # Безопасное извлечение данных
    ahp_data = config.get('ahp', {})
    game_data = config.get('game', {})

    ahp_matrix = ahp_data.get('comparison_matrix')
    game_matrix = game_data.get('payoff_matrix')

    if ahp_matrix is None or game_matrix is None:
        st.sidebar.error("В YAML не найдены ключи `ahp.comparison_matrix` или `game.payoff_matrix`")
        with st.sidebar.expander("Debug: структура файла"):
            st.json(config)
        st.stop()

    # 1. Заполняем названия каналов
    if 'channels' in ahp_data:
        st.session_state['channels_input'] = ", ".join(ahp_data['channels'])

    # 2. Заполняем виджеты АИИ (только верхний треугольник — нижний вычисляется симметрично)
    n = len(ahp_matrix)
    for i in range(n):
        for j in range(i + 1, n):
            st.session_state[f"ahp_{i}_{j}"] = float(ahp_matrix[i][j])

    # 3. Заполняем виджеты Игры
    for i in range(len(game_matrix)):
        for j in range(len(game_matrix[i])):
            st.session_state[f"game_{i}_{j}"] = float(game_matrix[i][j])

    # 4. Обновляем размеры матриц
    st.session_state['rows_game'] = len(game_matrix)
    st.session_state['cols_game'] = len(game_matrix[0])

    st.sidebar.success(f"Сценарий '{config.get('name', scenario)}' загружен!")
    st.rerun()



# Вкладка 1: АИИ
st.header("1. Оценка каналов (АИИ)")
st.markdown("Введите матрицу попарных сравнений каналов (например, SEO, SMM, Ads).")

channels = st.text_input(
    "Названия каналов через запятую",
    value=st.session_state['channels_input'],
    key="channels_input"
)
n_channels = len([c.strip() for c in channels.split(',') if c.strip()])

st.subheader("Матрица сравнения")
matrix_ahp = []
cols = st.columns(n_channels)
for i in range(n_channels):
    row = []
    for j in range(n_channels):
        if i == j:
            val = 1.0
        elif j < i:
            val = 1.0 / matrix_ahp[j][i]  # Симметрия
        else:
            val = cols[j].number_input(
                f"Канал {i+1} к Каналу {j+1}",
                min_value=0.1,
                max_value=9.0,
                value=1.0,
                step=0.1,
                key=f"ahp_{i}_{j}"
            )
        row.append(val)
    matrix_ahp.append(row)

if st.button("Рассчитать АИИ"):
    try:
        res = run_ahp(matrix_ahp)
        cr_icon = '' if res['is_consistent'] else '(нестабильно)'
        st.success(f"Индекс согласованности (CR): {res['consistency_ratio']:.3f} {cr_icon}")

        df = pd.DataFrame({
            "Канал": [c.strip() for c in channels.split(',')],
            "Вес (Приоритет)": [f"{w:.3f}" for w in res['weights']]
        })
        st.table(df)
    except Exception as e:
        st.error(f"Ошибка валидации: {e}")


# Вкладка 2: Матричная Игра
st.header("2. Распределение бюджета (Игра с конкурентом)")
st.markdown("Платежная матрица (выигрыш нашей компании в долях рынка). Строки — наши стратегии, Столбцы — стратегии конкурента.")

rows_game = st.number_input(
    "Кол-во наших стратегий", 1, 10,
    value=st.session_state['rows_game'],
    key="rows_game"
)
cols_game = st.number_input(
    "Кол-во стратегий конкурента", 1, 10,
    value=st.session_state['cols_game'],
    key="cols_game"
)

matrix_game = []
for i in range(rows_game):
    row = []
    for j in range(cols_game):
        val = st.number_input(
            f"Выигрыш [{i+1},{j+1}]",
            value=0.0,
            key=f"game_{i}_{j}"
        )
        row.append(val)
    matrix_game.append(row)

if st.button("Найти Равновесие Нэша"):
    try:
        res = run_game(matrix_game)
        if res['equilibria_found'] > 0:
            st.success(f"Найдено равновесий: {res['equilibria_found']}")
            for idx, eq in enumerate(res['strategies']):
                st.subheader(f"Равновесие #{idx+1}")
                st.write("**Наша оптимальная стратегия:**", [f"{x:.2f}" for x in eq['player_1_strategy']])
                st.write("**Стратегия конкурента:**", [f"{x:.2f}" for x in eq['player_2_strategy']])
        else:
            st.warning("Равновесие в чистых/смешанных стратегиях не найдено.")
    except Exception as e:
        st.error(f"Ошибка: {e}")