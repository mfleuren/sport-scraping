import pandas as pd
from dataclasses import dataclass, field

@dataclass
class DashData:
    folder: str = "scraper_soccerway/dash/data/"
    points_by_player: pd.DataFrame = field(default=pd.DataFrame)
    points_by_coach: pd.DataFrame = field(default=pd.DataFrame)
    substitutions: pd.DataFrame = field(default=pd.DataFrame)
    all_rounds: list[int] = field(default=list[str])
    max_round: int = field(default=1)
    all_coaches: list[str] = field(default=list[str])
    all_clubs: list[str] = field(default=list[str])
    all_positions: list[str] = field(default=list[str])

    def __init__(self):
        self.load_points_by_coach_data()
        self.load_points_by_player_data()
        self.load_substitutions()

        self.all_rounds = self.points_by_player["Speelronde"].unique().tolist()
        self.max_round = self.points_by_player["Speelronde"].max()
        self.all_coaches = sorted(self.points_by_coach["Coach"].unique().tolist(), key=str.casefold)
        self.all_clubs = sorted(self.points_by_player["Team"].unique().tolist(), key=str.casefold)
        self.all_positions = ["K", "V", "M", "A"]

    def load_points_by_coach_data(self) -> pd.DataFrame:
        """Load data from a csv file"""

        data = pd.read_csv(self.folder + "points_coach.csv", sep=';')
        data["P_Totaal"] = data["P_Totaal"].round(2)

        self.points_by_coach = data

    def load_points_by_player_data(self) -> pd.DataFrame:
        """Load data from a csv file"""

        points = pd.read_csv(self.folder + "points_player.csv", sep=';')
        players = pd.read_csv(self.folder + "dim_players.csv", sep=';')
        data = pd.merge(players, points, left_on="Naam", right_on="Speler")
        data = data[data["Positie"].isin(["K", "V", "M", "A"])]

        self.points_by_player = data

    def load_substitutions(self) -> pd.DataFrame:
        self.substitutions =  pd.read_csv(self.folder + "substitutions.csv", sep=';')