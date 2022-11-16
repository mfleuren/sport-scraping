import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def generate_lineups(teams: pd.DataFrame) -> None:
    """Generate a plot containing the team lineups."""

    Y_POSITION_POS = {"K": 0.05, "V": 0.35, "M": 0.60, "A": 0.85}

    X_POSITION_COUNT = {
        1: np.linspace(0, 1, 3)[1:-1],
        2: np.linspace(0, 1, 4)[1:-1],
        3: np.linspace(0, 1, 5)[1:-1],
        4: np.linspace(0, 1, 6)[1:-1],
        5: np.linspace(0, 1, 7)[1:-1],
    }

    Y_JITTER = {
        1: [0],
        2: [0, 0],
        3: [0, 0.07, 0],
        4: [0, 0.07, 0.07, 0],
        5: [0, 0.07, 0.14, 0.07, 0],
    }

    fig, ax = plt.subplots(
        int(np.ceil(teams["Coach"].nunique() / 3)), 3, figsize=(21.0, 29.7)
    )
    plt.tight_layout()
    ax_idx = 0

    for coach, team in teams.groupby("Coach"):

        if ax.ndim == 1:
            plt.sca(ax[ax_idx % 3])
        else:
            plt.sca(ax[int(ax_idx / 3), ax_idx % 3])

        plt.title(f"Coach: {coach}", size=18)
        plt.axis("off")
        plt.gca().set_aspect(1)
        plt.plot([0, 1, 1, 0, 0], [1, 1, 0, 0, 1], "-", color="#C7C7C7")
        circle_r = np.linspace(0, np.pi, 50)
        plt.plot(
            0.5 + 0.2 * np.cos(circle_r),
            1 - 0.2 * np.sin(circle_r),
            "-",
            color="#C7C7C7",
        )
        plt.plot([0.2, 0.2, 0.8, 0.8], [0, 0.2, 0.2, 0], "-", color="#C7C7C7")
        plt.plot(
            0.5 + 0.1 * np.cos(circle_r),
            0.2 + 0.1 * np.sin(circle_r),
            "-",
            color="#C7C7C7",
        )

        for _, player in team.iterrows():

            players_in_line = (
                team[team["Positie"] == player["Positie"]].copy().reset_index(drop=True)
            )
            current_player_idx_in_line = np.argmax(
                players_in_line["Naam"] == player["Naam"]
            )
            count_by_pos = players_in_line.shape[0]
            plt.text(
                x=X_POSITION_COUNT[count_by_pos][current_player_idx_in_line],
                y=Y_POSITION_POS[player["Positie"]]
                - Y_JITTER[count_by_pos][current_player_idx_in_line],
                s=f"{player['Naam']}\n({player['Team'].capitalize()})",
                size=12,
                ha="center",
            )

        ax_idx += 1
