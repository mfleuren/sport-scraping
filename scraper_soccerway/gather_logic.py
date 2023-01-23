import time
from tqdm import tqdm
import pandas as pd
from unidecode import unidecode
from datetime import datetime

from scraper_soccerway import gather, config
from scraper_soccerway.competition_data import CompetitionData


def construct_url(fmt_url: str, team: str, id: str) -> str:
    return fmt_url.format(base_url=config.BASE_URL, team_name=team, team_id=id)


def update_matches(data: CompetitionData) -> CompetitionData:
    """Loop through all tournament stages and update match dates and match URLs."""

    if data.urls["matches"]:
        urls = data.dim_clubs["SW_TeamURL"].apply(lambda x: config.BASE_URL + x)
    else:
        urls = [data.urls["matches_group"], data.urls["matches_finals"]]
    
    for url in tqdm(urls, total=len(urls)):

        updated_matches = gather.extract_matches_from_html_tournament(url, chunk_size=3)
        data.matches = pd.concat([data.matches, updated_matches], ignore_index=True)

        time.sleep(config.DEFAULT_SLEEP_S)

    # If a match_id is duplicated, only keep the last entry (most up to date)
    duplicated_mask = data.matches.duplicated(subset=["url_match"], keep="last")
    data.matches = data.matches[~duplicated_mask]

    data.matches["Datum"] = pd.to_datetime(data.matches["Datum"])

    return data


def update_players(data: CompetitionData) -> CompetitionData:
    def check_duplicates(
        df: pd.DataFrame, diff_col: str = None, keep: str = "last"
    ) -> pd.Series:

        cols_to_drop_constant = [
            "Rugnummer",
            "Naam",
            "Naam_fix",
            "Positie_Order",
            "Team_Order",
            "Naam_Order",
        ]
        cols_to_drop = (
            [diff_col] + cols_to_drop_constant if diff_col else cols_to_drop_constant
        )
        columns_to_check = df.columns[~df.columns.isin(cols_to_drop)]
        duplicated_mask = df.duplicated(subset=columns_to_check, keep=keep)

        if not diff_col:
            return duplicated_mask

        if (duplicated_mask.sum() > 0) & (keep == "last"):
            print(f"Found {duplicated_mask.sum()} changes in column {diff_col}")

            all_duplicates_mask = df.duplicated(subset=columns_to_check, keep=False)
            changes = (
                df[all_duplicates_mask]
                .groupby("Naam")
                .agg({diff_col: ["first", "last"]})
            )

            for name, row in changes.iterrows():
                print(
                    f"\t{name:16s}\t{row[diff_col]['first']:>12s}  -->  {row[diff_col]['last']:12s}"
                )
        return duplicated_mask

    all_players = data.dim_players.copy()
    for _, row in tqdm(data.dim_clubs.iterrows(), total=data.dim_clubs.shape[0]):

        team_url = construct_url(
                data.urls["teams"], row["SW_Teamnaam"], row["SW_TeamID"]
            )
        if data.tournament:            
            players_for_club = gather.extract_front_squad_from_html(team_url)
        else:
            players_for_club = gather.extract_squad_from_html(team_url)
        players_for_club["Team"] = row["Team"]
        all_players = pd.concat([all_players, players_for_club], ignore_index=True)
        time.sleep(config.DEFAULT_SLEEP_S)

    # Remove completely duplicated rows
    duplicated_mask = check_duplicates(df=all_players)
    all_players = all_players[~duplicated_mask].copy()

    # Check for players that changed position - keep the original row
    duplicated_mask_pos = check_duplicates(
        df=all_players, diff_col="Positie", keep="first"
    )
    all_players = all_players[~duplicated_mask_pos].copy()

    # Check for players that changed club - keep the new row
    duplicated_mask_team = check_duplicates(
        df=all_players, diff_col="Team", keep="last"
    )
    all_players = all_players[~duplicated_mask_team].copy()

    all_players["Naam_fix"] = all_players.apply(lambda x: unidecode(x["Naam"]), axis=1)
    data.dim_players = all_players.sort_values(by="SW_ID")

    return data


def process_teammodifications(data: CompetitionData, gameweek: int) -> CompetitionData:
        """Process substitutions and append the complete teams to the dataclass."""

        teams_new = data.chosen_teams[data.chosen_teams['Speelronde'] == gameweek-1].copy()
        teams_new['Speelronde'] = gameweek
        if 'Positie' in teams_new.columns:
            teams_new.drop(['Positie', 'Team', 'Link'], axis=1, inplace=True)

        # Process substitutions
        subs = data.substitutions[data.substitutions['Speelronde']==gameweek].copy()
        if subs.shape[0] > 0:
            print(f"Processing substitutions, speelronde {gameweek}:")
        for _, row in subs.iterrows():
            sub_mask = (teams_new['Coach']==row['Coach']) & (teams_new['Speler']==row['Wissel_Uit'])
            teams_new.loc[sub_mask, 'Speler'] = row['Wissel_In']
            print(f"{row['Coach']} [{row['Wissel_Uit']} --> {row['Wissel_In']}]")

        # Process free substitutions
        subs = data.free_substitutions[data.free_substitutions['Speelronde']==gameweek].copy()
        if subs.shape[0] > 0:
            print(f"Processing free substitutions, speelronde {gameweek}:")
        for _, row in subs.iterrows():
            sub_mask = (teams_new['Coach']==row['Coach']) & (teams_new['Speler']==row['Wissel_Uit'])
            teams_new.loc[sub_mask, 'Speler'] = row['Wissel_In']
            print(f"{row['Coach']} [{row['Wissel_Uit']} --> {row['Wissel_In']}]")
        
        # Join chosen team and dim_players to get info on clubs and positions
        data.dim_players['Naam_fix'] = data.dim_players.apply(lambda x: unidecode(x['Naam']), axis=1)
        players = data.dim_players.set_index('Naam_fix')[['Positie', 'Team', 'Link']].copy()
        teams_new = teams_new.join(players, on='Speler')

        data.chosen_teams = pd.concat([data.chosen_teams, teams_new], ignore_index=True)

        return data


def create_full_team_selections(data: CompetitionData, game_week: int) -> CompetitionData:

    data = process_teammodifications(data, game_week)

    data.chosen_teams = pd.merge(
        left=data.chosen_teams[["Coach", "Speler", "Speelronde"]],
        right=data.dim_players,
        left_on="Speler",
        right_on="Naam_fix",
        how="left",
    )

    return data


def determine_matches_to_scrape(data: CompetitionData) -> pd.DataFrame:
    """
    Determine which matches to scrape today. There are two criteria:
    (1) Match is finished, i.e. date is in the past
    (2) Match is not yet processed
    """

    data.matches = data.matches.sort_values(by='Datum')

    played_matches = data.matches["Datum"] < datetime.today().strftime('%Y-%m-%d')

    if data.match_events.shape[0] > 0:
        processed_matches = data.matches["url_match"].isin(data.match_events["Match_Url"])
    else:
        processed_matches = pd.Series([False] * len(played_matches))

    matches_to_scrape = data.matches[played_matches & ~processed_matches]

    return matches_to_scrape


def scrape_matches(data: CompetitionData, matches_to_scrape: pd.DataFrame, game_round: int) -> CompetitionData:
   
    matches_in_round = matches_to_scrape[matches_to_scrape["Cluster"] == game_round]
    print(game_round, matches_in_round)

    for _, match in tqdm(
        matches_in_round.iterrows(), total=matches_in_round.shape[0]
    ):
        try:
            match_events = gather.extract_match_events(match["url_match"], data.dim_players)
            match_events = match_events.join(data.matches.set_index('url_match')['Datum'], on='Match_Url')
            match_events["Speelronde"] = game_round
            data.match_events = pd.concat(
                [data.match_events, match_events], ignore_index=True
            )
            time.sleep(config.DEFAULT_SLEEP_S)
        except gather.MatchPostponedWarning:
            print(f"Match {match['url_match']} not processed.")

    return data
