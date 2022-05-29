import requests
import pandas as pd
from unidecode import unidecode
import time
import os
from dotenv import load_dotenv

from utility.result_objects import StageResults


load_dotenv()


def construct_pcs_url(epithet: str) -> str:
    """Construct the URL for PCS based on defaults and match-specific epithet."""
    url = f"{os.getenv('SCRAPER_PCS_BASE_URL')}/{epithet}/{os.getenv('COMPETITION_YEAR')}/result"
    return url


def construct_pcs_stage_url(epithet: str) -> str:
    """Construct the URL for PCS based on defaults and match-specific epithet."""
    url = f"{os.getenv('SCRAPER_PCS_BASE_URL')}/{os.getenv('COMPETITION_NAME').lower()}/{os.getenv('COMPETITION_YEAR')}/{epithet}/result"
    return url


def scrape_website(results: StageResults, match: pd.Series, stage_race: bool = False) -> StageResults:

    if stage_race:
        url = construct_pcs_stage_url(match['URL_EPITHET'])
    else:
        url = construct_pcs_url(match['URL_EPITHET'])

    result = requests.get(url)
    statuscode = result.status_code

    if statuscode == 200 and stage_race:
        result_table = read_result_table_stage(result.text, match)
    elif statuscode == 200 and not stage_race:
        result_table = read_result_table(result.text, match)
    else:
        print(f'Website {url} could not be accessed; status code {statuscode}')

    results.stage_results.append(result_table)

    time.sleep(int(os.getenv('SCRAPER_SLEEP_DELAY_IN_SEC')))

    return results


def read_result_table(html_text: str, match: pd.Series) -> pd.DataFrame:
    """Read the results from the table found in HTML input"""
    table_list = pd.read_html(html_text)
    results_table = clean_results_table(table_list[0], match)

    return results_table


def read_result_table_stage(html_text: str, match: pd.Series) -> pd.DataFrame:
    """Read the different result tables from the HTML input"""

    all_result_tables = pd.DataFrame()

    table_list = pd.read_html(html_text)
    rankings = ['STAGE', 'GC', 'SPRINT', 'KOM', 'YOUTH']
    ranking_exists = match[rankings].values
    for ranking, exists, idx in zip(rankings, ranking_exists, range(len(rankings))):

        if exists:
            result_table = clean_results_table(table_list[idx], match)

            if match['MATCH'] != 22:
                result_table['RANKING'] = 'stage_' + ranking.lower()
            else:
                result_table['RANKING'] = 'gc_' + ranking.lower()

            all_result_tables = pd.concat([all_result_tables, result_table], ignore_index=True)

    return all_result_tables
        
    

def clean_results_table(raw_table: pd.DataFrame, match: pd.Series) -> pd.DataFrame:
    """Return a cleaned table with results."""

    results_table = raw_table.copy()

    # Remove TEAM from rider name
    results_table['RIDER'] = results_table.apply(lambda x: x['Rider'].replace(x['Team'], ''), axis=1)

    # Convert name characters to unicode
    results_table['RIDER'] = results_table.apply(lambda x: unidecode(x['RIDER']), axis=1)

    # Split ridername in surname and firstname
    results_table['SURNAME'] = (results_table['RIDER']
                                .str.extract('([A-Z ]*)')[0]
                                .replace('[A-Z]$', '', regex=True)
                                .str.strip()
                                )
    results_table['FIRSTNAME'] = results_table.apply(lambda x: x['RIDER'].replace(x['SURNAME'], '').strip(), axis=1)

    # Rename essential columns to ALLCAPS
    results_table.rename({'Team':'TEAM', 'Age':'AGE', 'Rnk':'RNK'}, axis=1, inplace=True)

    # Add match information
    results_table['MATCH'] = match['MATCH']

    if 'LEVEL' in match.index:
        results_table['MATCH_LEVEL'] = match['LEVEL']
        COLUMNS_TO_KEEP = ['RNK', 'RIDER', 'FIRSTNAME', 'SURNAME', 'TEAM', 'MATCH', 'MATCH_LEVEL']   
        return results_table[COLUMNS_TO_KEEP]
    else: 
        COLUMNS_TO_KEEP = ['RNK', 'RIDER', 'FIRSTNAME', 'SURNAME', 'TEAM', 'MATCH']   
        return results_table[COLUMNS_TO_KEEP]