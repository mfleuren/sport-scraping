import pandas as pd
from dataclasses import dataclass, field


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
        
        for gameweek in self.gameweeks:
            points = df[df['Speelronde']==gameweek]
            print('points shape', points.shape)
            points_by_coach = (points
                .groupby('Coach', as_index=False)['P_Totaal']
                .sum()
                .sort_values(by='P_Totaal', ascending=False)
                .reset_index(drop=True)
                )
            points_by_coach['Stand'] = points_by_coach.index + 1

            table = [f'[b][u]Uitslag speelronde {gameweek}.[/u][/b]']
            table_header = f'[tr][td][b]Positie[/b][/td][td][b]Coach[/b][/td][td][b]Punten[/b][/td][/tr]'
            table_body = []
            for _, row in points_by_coach.iterrows():
                table_body.append(f"[tr][td]{row['Stand']}[/td][td]{row['Coach']}[/td][td]{row['P_Totaal']:.2f}[/td][/tr]")
            table.append(f"[table]{table_header}{''.join(table_body)}[/table]")

            self.round_ranking.append(''.join(table))


    def create_general_ranking(self, points: pd.DataFrame, subs: pd.DataFrame):
        """Create a string containing a formatted table with the general ranking after a given round.""" 

        points_by_coach = (points
            .copy()
            .groupby('Coach', as_index=False)['P_Totaal']
            .sum()
            .sort_values(by='P_Totaal', ascending=False)
            .reset_index(drop=True)
            )
        points_by_coach['Stand'] = points_by_coach.index + 1

        subs_by_coach = (subs[subs['Speelronde'] <= self.gameweeks[-1]]
            .copy()
            .groupby('Coach')['Wissel_In']
            .count()
            )
        subs_by_coach.name = 'N_Wissels'
        print(subs_by_coach)
        points_by_coach = points_by_coach.join(subs_by_coach, on='Coach')
        print(points_by_coach)
        points_by_coach['Minpunten_Wissels'] = 0
        points_by_coach.loc[points_by_coach['N_Wissels'] > 3, 'Minpunten_Wissels'] =  -20 * points_by_coach.loc[points_by_coach['N_Wissels'] > 3, 'N_Wissels']      
        points_by_coach['P_AlgemeenKlassement'] = points_by_coach['P_Totaal'] + points_by_coach['Minpunten_Wissels']

        table = [f'[b][u]Algemeen klassement na speelronde {self.gameweeks[-1]}.[/u][/b]']
        table_header = f'[tr][td][b]Positie[/b][/td][td][b]Coach[/b][/td][td][b]Punten[/b][/td][/tr]'
        table_body = []
        for _, row in points_by_coach.iterrows():
            table_body.append(f"[tr][td]{row['Stand']}[/td][td]{row['Coach']}[/td][td]{row['P_AlgemeenKlassement']:.2f}[/td][/tr]")
        table.append(f"[table]{table_header}{''.join(table_body)}[/table]")

        self.general_ranking = ''.join(table)


    def create_teams_overview(self, df: pd.DataFrame):
        """Create a string containing formatted tables with the chosen teams after a given round."""

        chosen_teams = df[df['Speelronde'] == self.gameweeks[-1]].copy()
        chosen_teams['Positie'].fillna('X', inplace=True)
        chosen_teams['Positie_Order'] = chosen_teams['Positie'].map(dict({'K':0, 'V':1, 'M':2, 'A':3, '-':4}))
        section = [f'[b][u]Gekozen teams na speelronde {self.gameweeks[-1]}.[/u][/b]\n[spoiler]']
        
        
        for coach in sorted(chosen_teams['Coach'].unique(), key=str.casefold):
            section_body = []
            section_body.append(f'[b]{coach}[/b]')
            table_header = f'[tr][td][b]Positie[/b][/td][td][b]Speler[/b][/td][/tr]'
            
            coach_team = chosen_teams[chosen_teams['Coach']==coach].sort_values(by=['Positie_Order', 'Speler'])
            table_body = []
            for _, row in coach_team.iterrows():
                table_body.append(f"[tr][td]{row['Positie']}[/td][td]{row['Speler']}[/td][/tr]")
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

        table = [f'[b][u]Spelersdatabase na speelronde {self.gameweeks[-1]}.[/u][/b]']
        table_header = f'[tr][td]Club[/td][td]Speler[/td][td]Positie[/td][/tr]'
        table_body = []
        for _, row in players.iterrows():
            table_body.append(f"[tr][td]{row['Team']}[/td][td]{row['Naam_fix']}[/td][td]{row['Positie']}[/td][/tr]")
        table.append(f"[spoiler][table]{table_header}{''.join(table_body)}[/table][/spoiler]")

        self.players_overview = ''.join(table)

            




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
    