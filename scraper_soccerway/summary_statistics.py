import pandas as pd
import generate_figures

# Combine points and player data
points = pd.read_csv("results/2022_World-Cup/points_player.csv", sep=";")
points_g = points.groupby("Speler")["P_Totaal"].sum().sort_values(ascending=False)

players = pd.read_csv("results/2022_World-Cup/dim_players.csv", sep=";")
players.set_index("Naam", inplace=True)
players = players[["Positie", "Team"]]

df = points_g.to_frame().join(players).dropna().sort_values("P_Totaal", ascending=False)

# Get best players by position and nation
# Remove all players that score < x points
df_sel = df.loc[df.groupby(["Team", "Positie"])["P_Totaal"].idxmax()].copy()
df_sel = df_sel[df_sel["P_Totaal"] >= df_sel["P_Totaal"].median()].copy()

best_team_df = pd.DataFrame()
best_score = 0

for i in range(0, 5000):

    sample_team_df = pd.DataFrame()
    n_players = len(sample_team_df)

    while n_players < 11:
        sample = df_sel.sample(n=1, weights="P_Totaal").copy()
        sample_pos = sample["Positie"].item()

        if len(sample_team_df) == 0:
            sample_team_df = pd.concat([sample_team_df, sample])
            continue

        if sample.index.item() in sample_team_df.index:
            continue

        if sample["Team"].item() in sample_team_df["Team"].values:
            continue

        position_counts = sample_team_df["Positie"].value_counts()
        existing_positions = [
            position_counts.loc["K"] if "K" in position_counts.index else 0,
            position_counts.loc["V"] if "V" in position_counts.index else 0,
            position_counts.loc["M"] if "M" in position_counts.index else 0,
            position_counts.loc["A"] if "A" in position_counts.index else 0,
        ]
        allowed_positions = []

        if existing_positions[0] == 0:
            allowed_positions.append("K")

        # Tactics flow to allow V
        if existing_positions[1] >= 5:
            pass
        elif (  # 541
            (existing_positions[1] == 4)
            & (existing_positions[2] <= 4)
            & (existing_positions[3] <= 1)
        ):
            allowed_positions.append("V")
        elif (  # 532
            (existing_positions[1] == 4)
            & (existing_positions[2] <= 3)
            & (existing_positions[3] <= 2)
        ):
            allowed_positions.append("V")
        elif (  # 433
            (existing_positions[1] == 3)
            & (existing_positions[2] <= 3)
            & (existing_positions[3] <= 3)
        ):
            allowed_positions.append("V")
        elif (  # 442
            (existing_positions[1] == 3)
            & (existing_positions[2] <= 4)
            & (existing_positions[3] <= 2)
        ):
            allowed_positions.append("V")
        elif existing_positions[1] <= 2:
            allowed_positions.append("V")

        # Tactics flow to allow M
        if existing_positions[2] >= 5:
            pass
        elif (  # 451
            (existing_positions[2] == 4)
            & (existing_positions[1] <= 4)
            & (existing_positions[3] <= 1)
        ):
            allowed_positions.append("M")
        elif (  # 352
            (existing_positions[2] == 4)
            & (existing_positions[1] <= 3)
            & (existing_positions[3] <= 2)
        ):
            allowed_positions.append("M")
        elif (  # 442
            (existing_positions[2] == 3)
            & (existing_positions[1] <= 4)
            & (existing_positions[3] <= 2)
        ):
            allowed_positions.append("M")
        elif (  # 343
            (existing_positions[2] == 3)
            & (existing_positions[1] <= 3)
            & (existing_positions[3] <= 3)
        ):
            allowed_positions.append("M")
        elif (  # 541
            (existing_positions[2] == 3)
            & (existing_positions[1] <= 5)
            & (existing_positions[3] <= 1)
        ):
            allowed_positions.append("M")
        elif existing_positions[2] <= 2:
            allowed_positions.append("M")

        # Tactics flow to allow A
        if existing_positions[3] >= 3:
            pass
        elif (  # 343
            (existing_positions[3] == 2)
            & (existing_positions[1] <= 3)
            & (existing_positions[2] <= 4)
        ):
            allowed_positions.append("A")
        elif (  # 433
            (existing_positions[3] == 2)
            & (existing_positions[1] <= 4)
            & (existing_positions[2] <= 3)
        ):
            allowed_positions.append("A")
        elif (  # 532
            (existing_positions[3] == 1)
            & (existing_positions[1] <= 5)
            & (existing_positions[2] <= 3)
        ):
            allowed_positions.append("A")
        elif (  # 442
            (existing_positions[3] == 1)
            & (existing_positions[1] <= 4)
            & (existing_positions[2] <= 4)
        ):
            allowed_positions.append("A")
        elif (  # 352
            (existing_positions[3] == 1)
            & (existing_positions[1] <= 3)
            & (existing_positions[2] <= 5)
        ):
            allowed_positions.append("A")
        elif existing_positions[3] < 1:
            allowed_positions.append("A")

        if sample_pos in allowed_positions:
            sample_team_df = pd.concat([sample_team_df, sample])

        n_players = len(sample_team_df)

    if sample_team_df["P_Totaal"].sum() > best_score:
        print(
            f"Iteration {i} - Improved best score! New best score: {sample_team_df['P_Totaal'].sum():.2f}"
        )
        best_team_df = sample_team_df.copy()
        best_score = best_team_df["P_Totaal"].sum()

best_team = best_team_df
best_team["Naam"] = best_team.index
best_team["P_Totaal"] = best_team["P_Totaal"].round(2)
generate_figures.generate_single_lineup(best_team, "P_Totaal", "best_team.png")
