import pandas as pd

def load_points_by_coach_data(path: str) -> pd.DataFrame:
    """Load data from a csv file"""

    data = pd.read_csv(path, sep=';')

    data["P_Totaal"] = data["P_Totaal"].round(2)

    print(data.columns)

    return data

def load_points_by_player_data(folder: str) -> pd.DataFrame:
    """Load data from a csv file"""

    points = pd.read_csv(folder + "points_player.csv", sep=';')
    print(points.columns)
    players = pd.read_csv(folder + "dim_players.csv", sep=';')
    print(players.columns)
    data = pd.merge(players, points, left_on="Naam", right_on="Speler")
    print(data.columns)
    data = data[data["Positie"].isin(["K", "V", "M", "A"])]

    return data
