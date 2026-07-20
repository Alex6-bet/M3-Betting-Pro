import math
import random

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="M-3 Betting Pro",
    page_icon="🎯",
    layout="wide",
)


def poisson_probability(lmbda: float, goals: int) -> float:
    """Calcula la probabilidad de un resultado usando Poisson."""
    return math.exp(-lmbda) * (lmbda**goals) / math.factorial(goals)


def american_to_implied_probability(odds: int) -> float:
    """Convierte cuotas americanas a probabilidad implícita."""
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)

    return 100 / (odds + 100)


def run_simulation(
    home_goals_average: float,
    away_goals_average: float,
    home_corners_average: float,
    away_corners_average: float,
    simulations: int,
) -> dict:
    """Ejecuta simulaciones básicas de goles y córners."""

    home_wins = 0
    draws = 0
    away_wins = 0

    home_over_25_corners = 0
    away_over_25_corners = 0
    both_over_25_corners = 0

    home_over_35_corners = 0
    away_over_35_corners = 0
    both_over_35_corners = 0

    total_home_goals = 0
    total_away_goals = 0
    total_home_corners = 0
    total_away_corners = 0

    score_counts = {}

    for _ in range(simulations):
        home_goals = random.choices(
            population=range(9),
            weights=[
                poisson_probability(home_goals_average, goals)
                for goals in range(9)
            ],
        )[0]

        away_goals = random.choices(
            population=range(9),
            weights=[
                poisson_probability(away_goals_average, goals)
                for goals in range(9)
            ],
        )[0]

        home_corners = random.choices(
            population=range(16),
            weights=[
                poisson_probability(home_corners_average, corners)
                for corners in range(16)
            ],
        )[0]

        away_corners = random.choices(
            population=range(16),
            weights=[
                poisson_probability(away_corners_average, corners)
                for corners in range(16)
            ],
        )[0]

        total_home_goals += home_goals
        total_away_goals += away_goals
        total_home_corners += home_corners
        total_away_corners += away_corners

        if home_goals > away_goals:
            home_wins += 1
        elif home_goals == away_goals:
            draws += 1
        else:
            away_wins += 1

        if home_corners >= 3:
            home_over_25_corners += 1

        if away_corners >= 3:
            away_over_25_corners += 1

        if home_corners >= 3 and away_corners >= 3:
            both_over_25_corners += 1

        if home_corners >= 4:
            home_over_35_corners += 1

        if away_corners >= 4:
            away_over_35_corners += 1

        if home_corners >= 4 and away_corners >= 4:
            both_over_35_corners += 1

        score = f"{home_goals}-{away_goals}"
        score_counts[score] = score_counts.get(score, 0) + 1

    most_common_scores = sorted(
        score_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    return {
        "home_win": home_wins / simulations,
        "draw": draws / simulations,
        "away_win": away_wins / simulations,
        "home_goals": total_home_goals / simulations,
        "away_goals": total_away_goals / simulations,
        "home_corners": total_home_corners / simulations,
        "away_corners": total_away_corners / simulations,
        "home_over_25": home_over_25_corners / simulations,
        "away_over_25": away_over_25_corners / simulations,
        "both_over_25": both_over_25_corners / simulations,
        "home_over_35": home_over_35_corners / simulations,
        "away_over_35": away_over_35_corners / simulations,
        "both_over_35": both_over_35_corners / simulations,
        "scores": most_common_scores,
    }


st.title("🎯 M-3 Betting Pro")
st.caption("Monte Carlo Lab · Versión 1.1")

with st.sidebar:
    st.header("⚙️ Configuración")

    home_team = st.text_input("Equipo local", value="España")
    away_team = st.text_input("Equipo visitante", value="Francia")

    simulations = st.select_slider(
        "Número de simulaciones",
        options=[1_000, 5_000, 10_000, 25_000, 50_000, 100_000],
        value=50_000,
    )

    st.divider()
    st.caption("Los datos de esta versión se introducen manualmente.")


st.subheader(f"⚽ {home_team} vs {away_team}")

left, right = st.columns(2)

with left:
    st.markdown(f"### {home_team}")

    home_goals_average = st.number_input(
        "Goles esperados",
        min_value=0.10,
        max_value=5.00,
        value=1.45,
        step=0.05,
        key="home_goals",
    )

    home_corners_average = st.number_input(
        "Córners esperados",
        min_value=0.50,
        max_value=12.00,
        value=5.40,
        step=0.10,
        key="home_corners",
    )

with right:
    st.markdown(f"### {away_team}")

    away_goals_average = st.number_input(
        "Goles esperados",
        min_value=0.10,
        max_value=5.00,
        value=1.20,
        step=0.05,
        key="away_goals",
    )

    away_corners_average = st.number_input(
        "Córners esperados",
        min_value=0.50,
        max_value=12.00,
        value=4.50,
        step=0.10,
        key="away_corners",
    )


if st.button("☠️ Sacar veneno", type="primary", use_container_width=True):
    with st.spinner(f"Corriendo {simulations:,} simulaciones..."):
        results = run_simulation(
            home_goals_average=home_goals_average,
            away_goals_average=away_goals_average,
            home_corners_average=home_corners_average,
            away_corners_average=away_corners_average,
            simulations=simulations,
        )

    st.success("Simulación terminada.")

    st.subheader("Probabilidades del partido")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        f"Victoria {home_team}",
        f"{results['home_win']:.1%}",
    )

    col2.metric(
        "Empate",
        f"{results['draw']:.1%}",
    )

    col3.metric(
        f"Victoria {away_team}",
        f"{results['away_win']:.1%}",
    )

    st.subheader("Promedios simulados")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        f"Goles {home_team}",
        f"{results['home_goals']:.2f}",
    )

    col2.metric(
        f"Goles {away_team}",
        f"{results['away_goals']:.2f}",
    )

    col3.metric(
        f"Córners {home_team}",
        f"{results['home_corners']:.2f}",
    )

    col4.metric(
        f"Córners {away_team}",
        f"{results['away_corners']:.2f}",
    )

    st.subheader("Mercados de córners")

    corners_table = pd.DataFrame(
        {
            "Mercado": [
                f"{home_team} Over 2.5",
                f"{away_team} Over 2.5",
                "Ambos equipos Over 2.5",
                f"{home_team} Over 3.5",
                f"{away_team} Over 3.5",
                "Ambos equipos Over 3.5",
            ],
            "Probabilidad M-3": [
                results["home_over_25"],
                results["away_over_25"],
                results["both_over_25"],
                results["home_over_35"],
                results["away_over_35"],
                results["both_over_35"],
            ],
        }
    )

    corners_table["Probabilidad M-3"] = corners_table[
        "Probabilidad M-3"
    ].map(lambda value: f"{value:.1%}")

    st.dataframe(
        corners_table,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Marcadores más frecuentes")

    scores_table = pd.DataFrame(
        results["scores"],
        columns=["Marcador", "Simulaciones"],
    )

    scores_table["Probabilidad"] = (
        scores_table["Simulaciones"] / simulations
    ).map(lambda value: f"{value:.1%}")

    st.dataframe(
        scores_table,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Esta primera versión utiliza distribuciones Poisson independientes. "
        "Todavía no incluye alineaciones, lesiones, clima, cuotas ni dependencia "
        "entre el marcador y los córners."
    )
else:
    st.info(
        "Introduce los promedios esperados y pulsa “Sacar veneno” "
        "para ejecutar la simulación."
    )
