import pandas as pd

from scraper_soccerway import config

def tactics(teams: pd.DataFrame) -> None:
    
    for coach, data in teams.groupby('Coach'):
        K = (data['Positie'] == 'K').sum()
        V = (data['Positie'] == 'V').sum()
        M = (data['Positie'] == 'M').sum()
        A = (data['Positie'] == 'A').sum()
        special = data['Speler'].str.contains('!').sum()        

        try: 
            num_players = K + V + M + A + special
            assert not (num_players != 11), f'Team of {coach} does not have 11 players.' 
             
            tactic = f'{K}{V}{M}{A}'         
            assert not (tactic not in config.ALLOWED_TACTICS and special == 0), f'Team of {coach} plays a tactic that is not allowed: {tactic}'           
            
            unique_teams = data['Team'].nunique()
            assert not (unique_teams != 11 and special == 0), f"Team of {coach} has more than 1 player of the same team."
        except AssertionError as e:
            print(f'Error! {e}')
            print(data[['Speler', 'Team', 'Positie']])
        