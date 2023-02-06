from dataclasses import dataclass, field
from typing import Optional, Union
from distutils.util import strtobool
import pandas as pd
import os

import config
import gather

@dataclass
class CompetitionData:
    name: str
    year: int
    urls: dict
    tournament: bool 
    local_dir_input: str
    local_dir_result: str
    id: Optional[str] = field(init=False, repr=False)
    id_group: Optional[str] = field(init=False, repr=False)
    id_finals: Optional[str] = field(init=False, repr=False)
    nation: Optional[str] = field(init=False, repr=False)
    continent: Optional[str] = field(init=False, repr=False)   
    chosen_teams: Optional[pd.DataFrame] = field(init=False, repr=False)
    substitutions: Optional[pd.DataFrame] = field(init=False, repr=False)
    points_scheme: Optional[pd.DataFrame] = field(init=False, repr=False)
    points_player: Optional[pd.DataFrame] = field(init=False, repr=False)
    points_coach: Optional[pd.DataFrame] = field(init=False, repr=False)
    dim_clubs: Optional[pd.DataFrame] = field(init=False, repr=False)
    dim_players: Optional[pd.DataFrame] = field(init=False, repr=False)
    matches: Optional[pd.DataFrame] = field(init=False, repr=False)
    match_events: Optional[pd.DataFrame] = field(init=False, repr=False)    


    def __init__(self, name: str):
        settings = config.COMPETITION_SETTINGS[name]

        self.name = settings["NAME"]
        self.year = settings["YEAR"]
        self.urls = settings["URLS"]
        self.tournament = settings["TOURNAMENT"]
        self.local_dir_input = f"./inputs/{self.year}_{self.name}"
        self.local_dir_result = f"./results/{self.year}_{self.name}"

        if self.tournament:
            self.id_group = settings["ID_GROUP"]
            self.id_finals = settings["ID_FINALS"] 
            self.nation = settings["NATION"]
            self.continent = settings["CONTINENT"]
        
        elif self.tournament == False:
            self.id = settings["ID"]
            self.substitutions = pd.read_csv(
                os.path.join(self.local_dir_input, config.LOCAL_FILES["substitutions"]),
                sep=';'
                )
            self.free_substitutions = pd.read_csv(
                os.path.join(self.local_dir_input, config.LOCAL_FILES["substitutions_free"]),
                sep=';'
                )

        self.chosen_teams = self.load_file_from_input_or_results(
            os.path.join(self.local_dir_input, config.LOCAL_FILES["teams"]), 
            os.path.join(self.local_dir_result, config.LOCAL_FILES["teams"])
            )
        self.points_scheme = pd.read_csv(
            os.path.join(self.local_dir_input, config.LOCAL_FILES["points_scheme"]), 
            sep=';'
            )
        self.points_player = self.load_file_from_results(
            os.path.join(self.local_dir_result, config.LOCAL_FILES["points_player"])
        )
        self.points_coach = self.load_file_from_results(
            os.path.join(self.local_dir_result, config.LOCAL_FILES["points_coach"])
        )
        self.dim_clubs = self.load_clubs(
            os.path.join(self.local_dir_result, config.LOCAL_FILES["clubs"])
        )
        self.dim_players = self.load_file_from_results(
            os.path.join(self.local_dir_result, config.LOCAL_FILES["players"])
        )
        self.matches = self.load_file_from_results(
            os.path.join(self.local_dir_result, config.LOCAL_FILES["matches"])
        )
        self.match_events = self.load_file_from_results(
            os.path.join(self.local_dir_result, config.LOCAL_FILES["match_events"])
        )


    def load_file_from_input_or_results(self, 
        input_path: Union[str, os.PathLike], 
        result_path: Union[str, os.PathLike]
        ) -> pd.DataFrame:
        """
        Logic to determine which teams file to initialize:
        - If results file exists: use results
        - Else if input file exists: use inputs
        - Else: Error
        """

        try:
            if os.path.exists(result_path):
                df = pd.read_csv(result_path, sep=';')

                if 'Datum' in df.columns:
                    df['Datum'] = pd.to_datetime(df['Datum'], format='%d-%m-%Y')

                print(f'Loaded file {result_path} from result.')
                return df

            elif os.path.exists(input_path):
                df = pd.read_csv(input_path, sep=';')

                print(f'Loaded file {input_path} from input.')
                return df

            else:
                raise Exception(input_path, result_path)

        except Exception:
            print(f'Unexpected Exception. Files {input_path} and {result_path} both not found.')
            raise


    def load_file_from_results(self, path: Union[str, os.PathLike]) -> pd.DataFrame:
        """Load file from Results folder, if not exists pre-allocate empty DataFrame."""

        if os.path.exists(path):
            df = pd.read_csv(path, sep=';')

            if 'Datum' in df.columns:
                df['Datum'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d')

            print(f'Loaded file {path} from result, converted Datum column.')

            return df
            
        else: 

            df = pd.DataFrame()

            print(f'Could not find file {path} from result, allocated an empty DataFrame.')

            return df



    def save_files_to_results(self) -> None:
        """Save datafile to Results folder"""

        if self.matches.shape[0] != 0:
            self.matches.to_csv(
                os.path.join(self.local_dir_result, config.LOCAL_FILES["matches"]), 
                sep=';', 
                index=False
                )
            print('Saved matches data to disk.')

        if self.dim_players.shape[0] != 0:
            self.dim_players.to_csv(
                os.path.join(self.local_dir_result, config.LOCAL_FILES["players"]), 
                sep=';', 
                index=False
                )
            self.dim_players.to_csv(
                f'E:/DataScience/sport-scraping/scraper_soccerway/dash/data/{config.LOCAL_FILES["players"]}',
                sep=';',
                index=False
            )
            print('Saved players data to disk.')

        if self.chosen_teams.shape[0] != 0:
            self.chosen_teams.to_csv(
                os.path.join(self.local_dir_result, config.LOCAL_FILES["teams"]), 
                sep=';', 
                index=False
                )
            print('Saved chosen teams data to disk.')

        if self.points_player.shape[0] != 0:
            self.points_player.to_csv(
                os.path.join(self.local_dir_result, config.LOCAL_FILES["points_player"]), 
                sep=';', 
                index=False)
            self.points_player.to_csv(
                f'E:/DataScience/sport-scraping/scraper_soccerway/dash/data/{config.LOCAL_FILES["points_player"]}',
                sep=';',
                index=False
            )
            print('Saved points by player data to disk.')

        if self.points_coach.shape[0] != 0:
            self.points_coach.to_csv(
                os.path.join(self.local_dir_result, config.LOCAL_FILES["points_coach"]), 
                sep=';', 
                index=False
                )
            self.points_coach.to_csv(
                f'E:/DataScience/sport-scraping/scraper_soccerway/dash/data/{config.LOCAL_FILES["points_coach"]}',
                sep=';',
                index=False
            )    
            print('Saved points by coach data to disk.')

        if self.match_events.shape[0] != 0:
            self.match_events.to_csv(
                os.path.join(self.local_dir_result, config.LOCAL_FILES["match_events"]), 
                sep=';', 
                index=False
                )
            print('Saved match events data to disk.')

        if self.substitutions.shape[0] != 0:
            self.substitutions.to_csv(
                f'E:/DataScience/sport-scraping/scraper_soccerway/dash/data/{config.LOCAL_FILES["substitutions"]}',
                sep=';',
                index=False
            )
        
    
    def load_clubs(self, path: Union[str, os.PathLike]) -> pd.DataFrame:
        """Load the dimension table with club information, if it doesn't exist scrape it from Soccerway"""

        if os.path.exists(path):
            df = pd.read_csv(path, sep=';')
            print(f'Loaded file {path} from result.')
            return df
        else:

            if self.tournamenet:
                url = self.urls["start_teams"].format(
                    base_url=config.BASE_URL,
                    continent=self.continent,
                    name=self.name,
                    year=self.year,
                    nation=self.nation,
                    id_group=self.id_group
                )
            elif self.tournament == False:
                url = self.urls["start_teams"].format(
                    base_url=config.BASE_URL,
                    year=self.year,
                    id=self.id
                    )
            print(url)
            clubs = gather.extract_clubs_from_html(url)

            clubs.to_csv(path, sep=';', index=False)

            return clubs