import pandas as pd
import os
from dataclasses import dataclass, field

from competition_data import CompetitionData


@dataclass
class Message:
    gameweeks: list[int] = field(default_factory=list[int])
    substitution_table: list[str] = field(default_factory=list[str])
    round_ranking: list[str] = field(default_factory=list[str])
    general_ranking: str = field(default_factory=str)
    teams_overview: str = field(default_factory=str)
    players_overview: str = field(default_factory=str)

    def create_substitutions_table(self, df: pd.DataFrame):
        """Create a string containing a formatted table with substitutions by game round."""

        for gameweek in self.gameweeks:
            
            df['N_Wissel'] = df.groupby('Coach').cumcount()
            substitutions = df[df['Speelronde']==gameweek]

            if substitutions.shape[0] == 0:
                table = f'[b][u]Geen wissels in speelronde {gameweek}.[/u][/b]\n'

            else:
                table = [f'[b][u]Wissels speelronde {gameweek}.[/u][/b]']
                table_header = f'[tr][td][b]Speelronde[/b][/td][td][b]Coach[/b][/td][td][b]Speler IN[/b][/td][td][b]Speler UIT[/b][/td][td][b]Wissel #[/b][/td][/tr]'
                table_body = []
                for _,row in substitutions.iterrows():
                    table_body.append(f"[tr][td]{gameweek}[/td][td]{row['Coach']}[/td][td]{row['Wissel_In']}[/td][td]{row['Wissel_Uit']}[/td][td]{row['N_Wissel']+1}[/td][/tr]")
                table.append(f"[table]{table_header}{''.join(table_body)}[/table]")

            self.substitution_table.append(''.join(table))


    def create_round_ranking(self, df: pd.DataFrame):
        """Create a string containing a formatted table with ranking for a given round."""
        
        for game_week in self.gameweeks:

            points = df[df['Speelronde']==game_week]
            points_by_coach = (points
                .groupby('Coach', as_index=False)['P_Totaal']
                .sum()
                .sort_values(by='P_Totaal', ascending=False)
                .reset_index(drop=True)
                )
            points_by_coach['Stand'] = points_by_coach.index + 1

            table = [f'[b][u]Uitslag speelronde {game_week}.[/u][/b]']
            table_header = f'[tr][td][b]Positie[/b][/td][td][b]Coach[/b][/td][td][b]Punten[/b][/td][/tr]'
            table_body = []
            for _, row in points_by_coach.iterrows():
                table_body.append(f"[tr][td]{row['Stand']}[/td][td]{row['Coach']}[/td][td]{row['P_Totaal']:.2f}[/td][/tr]")
            table.append(f"[table]{table_header}{''.join(table_body)}[/table]")

            self.round_ranking.append(''.join(table))


    def create_general_ranking(self, points: pd.DataFrame, subs: pd.DataFrame = None):
        """Create a string containing a formatted table with the general ranking after a given round.""" 

        points_by_coach = (points
            .copy()
            .groupby('Coach', as_index=False)['P_Totaal']
            .sum()
            .sort_values(by='P_Totaal', ascending=False)
            .reset_index(drop=True)
            )

        if isinstance(subs, pd.DataFrame):
            subs_in_round = subs[subs['Speelronde'] <= points["Speelronde"].max()]
            subs_by_coach = (subs_in_round
                .copy()
                .groupby('Coach')['Wissel_In']
                .count()
                )
            subs_by_coach.name = 'N_Wissels'
            points_by_coach = points_by_coach.join(subs_by_coach, on='Coach')
            points_by_coach['Minpunten_Wissels'] = 0
            points_by_coach.loc[points_by_coach['N_Wissels'] > 3, 'Minpunten_Wissels'] =  -20 * (points_by_coach.loc[points_by_coach['N_Wissels'] > 3, 'N_Wissels'] - 3)      
            points_by_coach['P_AlgemeenKlassement'] = points_by_coach['P_Totaal'] + points_by_coach['Minpunten_Wissels']
        else:
            points_by_coach['P_AlgemeenKlassement'] = points_by_coach['P_Totaal']

        point_by_coach_summed = points_by_coach.groupby('Coach', as_index=False)['P_AlgemeenKlassement'].sum()

        if len(self.gameweeks) > 0:
            table = [f'[b][u]Algemeen klassement na speelronde {self.gameweeks[-1]}.[/u][/b]']
        else:
            table = [f'[b][u]Algemeen klassement.[/u][/b]']
        table_header = f'[tr][td][b]Positie[/b][/td][td][b]Coach[/b][/td][td][b]Punten[/b][/td][/tr]'
        table_body = []
        for idx, row in point_by_coach_summed.sort_values(by='P_AlgemeenKlassement', ascending=False).reset_index(drop=True).iterrows():
            table_body.append(f"[tr][td]{idx+1}[/td][td]{row['Coach']}[/td][td]{row['P_AlgemeenKlassement']:.2f}[/td][/tr]")
        table.append(f"[table]{table_header}{''.join(table_body)}[/table]")

        self.general_ranking = ''.join(table)


    def create_teams_overview(self, df: pd.DataFrame):
        """Create a string containing formatted tables with the chosen teams after a given round."""

        if len(self.gameweeks) > 0:
            section = [f'[b][u]Gekozen teams na speelronde {self.gameweeks[-1]}.[/u][/b]\n[spoiler]']
        else:
            section = [f'[b][u]Gekozen teams.[/u][/b]\n[spoiler]']

        for coach in sorted(df["Coach"].unique(), key=str.casefold):

            # Data formatting
            df_coach = df[(df["Coach"] == coach)].copy()
            dfg = df_coach.groupby(["Speler", "Positie"]).agg({"P_Totaal":"sum", "Speelronde":["min", "max"]})

            dfg.columns = ['_'.join(col) for col in dfg.columns.values]

            dfg_sel = dfg[dfg["Speelronde_max"] == dfg["Speelronde_max"].max()].copy().reset_index()

            dfg_sel["Aantal_rondes"] = dfg_sel["Speelronde_max"] - dfg_sel["Speelronde_min"] + 1
            dfg_sel["Puntengemiddelde"] = (dfg_sel["P_Totaal_sum"] / dfg_sel["Aantal_rondes"]).round(2)
            dfg_sel["Positie_Order"] = dfg_sel["Positie"].map(dict({'K':0, 'V':1, 'M':2, 'A':3, '-':4}))

            # Append section
            section_body = []
            section_body.append(f'[b]{coach}[/b]')
            table_header = """
            [tr]
            [td][b]Positie[/b][/td]
            [td][b]Speler[/b][/td]
            [td][b]Punten Totaal[/b][/td]
            [td][b]Aantal Speelrondes[/b][/td]
            [td][b]Punten Gemiddeld[/b][/td]
            [/tr]
            """
            table_body = []
            for _, row in dfg_sel.sort_values(["Positie_Order", "Speler"]).iterrows():
                table_body.append(f"[tr][td]{row['Positie']}[/td][td]{row['Speler']}[/td][td]{row['P_Totaal_sum']:.2f}[/td][td]{row['Aantal_rondes']}[/td][td]{row['Puntengemiddelde']:.2f}[/td][/tr]")

            section_body.append(f"[spoiler][table]{table_header}{''.join(table_body)}[/table][/spoiler]")
            section.append(''.join(section_body))
        section.append('[/spoiler]')

        self.teams_overview = ''.join(section)


    def create_players_overview(self, df: pd.DataFrame):
        """Create a string containing a formatted table with all known players in the database, their clubs and their positions."""

        df['Positie_Order'] = df['Positie'].map(dict({'K':0, 'V':1, 'M':2, 'A':3}))
        df['Team_Order'] = df['Team'].str.lower()
        df['Naam_Order'] = df['Naam_fix'].str.lower()
        players = df.sort_values(by=['Team_Order', 'Positie_Order', 'Naam_Order'])

        if len(self.gameweeks) > 0:
            table = [f'[b][u]Spelersdatabase na speelronde {self.gameweeks[-1]}.[/u][/b]']
        else: 
            table = [f'[b][u]Spelersdatabase.[/u][/b]']
        table_header = f'[tr][td]Club[/td][td]Speler[/td][td]Positie[/td][/tr]'
        table_body = []
        for _, row in players.iterrows():
            table_body.append(f"[tr][td]{row['Team']}[/td][td]{row['Naam_fix']}[/td][td]{row['Positie']}[/td][/tr]")
        table.append(f"[spoiler][table]{table_header}{''.join(table_body)}[/table][/spoiler]")

        self.players_overview = ''.join(table)

def create_message(data: CompetitionData, gameweeks: list[int]) -> str:
    """Process the data and generate a message to post on a internet forum."""

    message = Message(gameweeks=gameweeks)
    message.create_substitutions_table(data.substitutions.copy())
    message.create_round_ranking(data.points_coach.copy())
    message.create_general_ranking(data.points_coach.copy(), data.substitutions.copy())
    message.create_teams_overview(data.points_coach.copy())
    message.create_players_overview(data.dim_players.copy())

    single_message = []
    for idx,_ in enumerate(gameweeks):
        single_message.append(message.substitution_table[idx])
        single_message.append(message.round_ranking[idx])
    single_message.append(message.general_ranking)
    single_message.append(message.teams_overview)
    single_message.append(message.players_overview)
    single_message.append(f"Bekijk alle statistieken en overzichten op {os.getenv('DASH_URL')}.")

    final_message = ''.join(single_message)

    return final_message        


if __name__ == '__main__':
    substitutions = pd.read_csv('E:\\DataScience\\sport-scraping\\inputs\\2022_Eredivisie\\substitutions.csv', sep=';')
    points_player = pd.read_csv('E:\\DataScience\\sport-scraping\\results\\2022_Eredivisie\\points_player.csv', sep=';')
    points_coach = pd.read_csv('E:\\DataScience\\sport-scraping\\results\\2022_Eredivisie\\points_coach.csv', sep=';')
    chosen_teams = pd.read_csv('E:\\DataScience\\sport-scraping\\results\\2022_Eredivisie\\teams.csv', sep=';')
    dim_players = pd.read_csv('E:\\DataScience\\sport-scraping\\results\\2022_Eredivisie\\dim_players.csv', sep=';')

    gameweeks = [1]
    message = Message(gameweeks=gameweeks)
    message.create_substitutions_table(substitutions)
    message.create_round_ranking(points_coach)
    message.create_general_ranking(points_coach, substitutions)
    message.create_teams_overview(chosen_teams)
    message.create_players_overview(dim_players)
    