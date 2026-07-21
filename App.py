import math
import random

import pandas as pd
import streamlit as st
from engine import run_simulation


st.set_page_config(
    page_title="M-3 Betting Pro v1.1",
    page_icon="🎯",
    layout="wide",
)


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
