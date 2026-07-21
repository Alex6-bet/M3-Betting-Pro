import math
import random

import pandas as pd
import streamlit as st
from engine import analyze_bet_value, run_simulation


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
        st.session_state["last_results"] = results
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
st.divider()
st.subheader("🎯 Detector de valor EV")
st.caption("Compara la probabilidad calculada por M-3 con la cuota de la casa.")
last_results = st.session_state.get("last_results")

market_probabilities = {
    "Introducir probabilidad manualmente": None,
}

if last_results:
    market_probabilities.update(
        {
            "Victoria equipo local": last_results["home_win"] * 100,
            "Empate": last_results["draw"] * 100,
            "Victoria equipo visitante": last_results["away_win"] * 100,
            "Local Over 2.5 córners": last_results["home_over_25"] * 100,
            "Visitante Over 2.5 córners": last_results["away_over_25"] * 100,
            "Ambos Over 2.5 córners": last_results["both_over_25"] * 100,
            "Local Over 3.5 córners": last_results["home_over_35"] * 100,
            "Visitante Over 3.5 córners": last_results["away_over_35"] * 100,
            "Ambos Over 3.5 córners": last_results["both_over_35"] * 100,
        }
    )

selected_market = st.selectbox(
    "Mercado para analizar",
    options=list(market_probabilities.keys()),
)

automatic_probability = market_probabilities[selected_market]
ev_col1, ev_col2, ev_col3 = st.columns(3)

with ev_col1:
    if automatic_probability is None:
        model_probability_pct = st.number_input(
            "Probabilidad M-3 (%)",
            min_value=0.1,
            max_value=99.9,
            value=75.0,
            step=0.1,
            key="ev_probability_manual",
        )
    else:
        model_probability_pct = float(automatic_probability)
        st.metric(
            "Probabilidad M-3",
            f"{model_probability_pct:.1f}%",
        )

with ev_col2:
    american_odds = st.number_input(
        "Cuota americana",
        min_value=-5000,
        max_value=5000,
        value=-150,
        step=5,
        key="ev_odds",
    )

with ev_col3:
    stake = st.number_input(
        "Cantidad apostada ($)",
        min_value=1.0,
        value=100.0,
        step=10.0,
        key="ev_stake",
    )

if st.button("📊 Analizar valor", use_container_width=True):
    if american_odds == 0:
        st.error("La cuota americana no puede ser 0.")
    else:
        value = analyze_bet_value(
            model_probability_pct / 100,
            american_odds,
            stake,
        )

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric(
            "Probabilidad implícita",
            f"{value['implied_probability']:.1%}",
        )

        metric2.metric(
            "Edge M-3",
            f"{value['edge']:.1%}",
        )

        metric3.metric(
            "Valor esperado",
            f"${value['expected_value']:+.2f}",
        )

        metric4.metric(
            "Cuota decimal",
            f"{value['decimal_odds']:.2f}",
        )

        if value["has_value"]:
            st.success("✅ HAY VALOR MATEMÁTICO")
        else:
            st.warning("⚠️ NO HAY VALOR MATEMÁTICO")