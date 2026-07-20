import math
import random


def poisson_probability(lmbda: float, goals: int) -> float:
    """Calcula la probabilidad de un resultado usando Poisson."""
    return math.exp(-lmbda) * (lmbda**goals) / math.factorial(goals)


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

    goal_probabilities_home = [
        poisson_probability(home_goals_average, goals)
        for goals in range(9)
    ]

    goal_probabilities_away = [
        poisson_probability(away_goals_average, goals)
        for goals in range(9)
    ]

    corner_probabilities_home = [
        poisson_probability(home_corners_average, corners)
        for corners in range(16)
    ]

    corner_probabilities_away = [
        poisson_probability(away_corners_average, corners)
        for corners in range(16)
    ]

    for _ in range(simulations):
        home_goals = random.choices(
            population=range(9),
            weights=goal_probabilities_home,
        )[0]

        away_goals = random.choices(
            population=range(9),
            weights=goal_probabilities_away,
        )[0]

        home_corners = random.choices(
            population=range(16),
            weights=corner_probabilities_home,
        )[0]

        away_corners = random.choices(
            population=range(16),
            weights=corner_probabilities_away,
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