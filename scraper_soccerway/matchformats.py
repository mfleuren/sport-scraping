import time
import os 
import sys
sys.path.append(os.getcwd())

from utility.result_objects import CompetitionData
import config as cfg
import gather 

if __name__ == '__main__':

    data = CompetitionData()
    
    for idx,row in data.dim_clubs.iterrows():
        match_url = cfg.URLS['matches'].format(club_name=row['SW_Teamnaam'], club_id=row['SW_TeamID'])
        print(f'Started scraping {match_url}')

        html_string = gather.open_website_in_client(match_url)

        matches_for_club = gather.extract_matches_from_html(html_string)
        data.matches = data.matches.append(matches_for_club)

        # If a match_id is duplicated, only keep the last entry
        duplicated_mask = data.matches.duplicated(subset=['url_match'], keep='last')
        data.matches = data.matches[~duplicated_mask]

        # Sort matches by date
        data.matches = data.matches.sort_values(by='Datum')
        print(f'Finished scraping {match_url}')

        time.sleep(3)

    data.save_files_to_results()
