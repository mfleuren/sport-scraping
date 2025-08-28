import requests
import pandas as pd
import numpy as np
from unidecode import unidecode
import time
import os
from dotenv import load_dotenv
from operator import itemgetter
from typing import List

import sys
sys.path.append(os.getcwd())
from utility.result_objects import StageResults


try:
    load_dotenv()
except:
    print("Failed to load .env")


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

    table_list = pd.read_html(html_text)

    # Only keep tables with specific indices
    if not match["TTT"]:

        all_result_tables = pd.DataFrame()

        cleaned_table_list = itemgetter(*[0, 1, 2, 5, -4])(table_list)
        all_rankings = ['STAGE', 'GC', 'SPRINT', 'KOM', 'YOUTH']
        ranking_exists = match[all_rankings].values
        ranking_val = [all_rankings[i] for i,y in enumerate(ranking_exists) if y]
        for idx, val in enumerate(ranking_val):

            result_table = clean_results_table(cleaned_table_list[idx], match)

            if match['MATCH'] != 22:
                if val == "STAGE":
                    # Skip stage result for GC
                    pass
                result_table['RANKING'] = f"stage_{val.lower()}"
            else:
                result_table['RANKING'] = f"gc_{val.lower()}"

            all_result_tables = pd.concat([all_result_tables, result_table], ignore_index=True)

        return all_result_tables
    
    else:

        number_of_participating_teams = table_list[-1].shape[0]
        print("Number of participating teams: ", number_of_participating_teams)

        ttt_table_indices = list(range(0, number_of_participating_teams)) + [len(table_list)-1]

        # GC/Sprint/KOM/Youth
        other_indices = list(range(number_of_participating_teams, number_of_participating_teams + 4))

        # Get stage result
        ttt_tables = itemgetter(*ttt_table_indices)(table_list)
        result_table = clean_ttt_table(ttt_tables, match)
        result_table["RANKING"] = "stage_stage"
        all_result_tables = result_table

        # Get the gc results
        gc_tables = itemgetter(*other_indices)(table_list)
        for idx, val in enumerate(["GC", "SPRINT", "KOM", "YOUTH"]):
            result_table = clean_results_table(gc_tables[idx], match)
            result_table["RANKING"] = f"stage_{val.lower()}"
            all_result_tables = pd.concat([all_result_tables, result_table], ignore_index=True)
        
        return all_result_tables                              
        

def clean_results_table(raw_table: pd.DataFrame, match: pd.Series) -> pd.DataFrame:
    """Return a cleaned table with results."""

    results_table = raw_table.copy()

    # Remove TEAM from rider name
    results_table['RIDER'] = results_table.apply(lambda x: x['Rider'].replace(x['Team'], ''), axis=1)

    # Convert name characters to unicode
    results_table['RIDER'] = results_table.apply(lambda x: unidecode(x['RIDER']), axis=1)

    # Remove PCS added crap
    results_table['RIDER'] = results_table['RIDER'].str.replace('fav_gc', '')

    # Remove trailing spaces
    results_table['RIDER'] = results_table['RIDER'].str.strip()

    # Remove rows without rider name 
    # NOTE: this can happen when PCS adds messages into the result table
    results_table = results_table[results_table["RIDER"] != ""]

    # Rename essential columns to ALLCAPS
    results_table.rename({'Team':'TEAM', 'Age':'AGE', 'Rnk':'RNK'}, axis=1, inplace=True)

    # Add match information
    results_table['MATCH'] = match['MATCH']

    if 'LEVEL' in match.index:
        results_table['MATCH_LEVEL'] = match['LEVEL']
        COLUMNS_TO_KEEP = ['RNK', 'RIDER', 'TEAM', 'MATCH', 'MATCH_LEVEL']   
        return results_table[COLUMNS_TO_KEEP]
    else: 
        COLUMNS_TO_KEEP = ['RNK', 'RIDER', 'TEAM', 'MATCH']   
        return results_table[COLUMNS_TO_KEEP]


def clean_ttt_table(raw_tables: List[pd.DataFrame], match: pd.Series) -> pd.DataFrame:
    """Clean table script specifically for TTT."""

    # Combine results of all teams and assign RNK
    results_table = pd.concat([t.assign(RNK=i+1) for i, t in enumerate(raw_tables) if t.shape[1] == 3])

    # Clean rider names using participating teams
    participating_teams = raw_tables[-1]["Team"].to_list()

    # Escape | in team name (f*ck Visma Lease A Bike)
    participating_teams = [x.replace("|", r"\|") if "|" in x else x for x in participating_teams ]

    results_table["RIDER"] = results_table[0].str.replace("|".join(participating_teams + ["fav_gc"] + [r" \+[\d]+:[\d]+"]), "", regex=True)
    results_table["TEAM"] = results_table[0].str.extract(rf'({"|".join(participating_teams)})')

    # Convert name characters to unicode
    results_table['RIDER'] = results_table.apply(lambda x: unidecode(x['RIDER']), axis=1)

    # Add match information
    results_table['MATCH'] = match['MATCH']

    COLUMNS_TO_KEEP = ['RNK', 'RIDER', 'TEAM', 'MATCH'] 
    return results_table[COLUMNS_TO_KEEP]


if __name__ == '__main__':

    url = 'https://www.procyclingstats.com/race/vuelta-a-espana/2025/stage-5/result'
    result = requests.get(url)
    raw_tables = pd.read_html(result.text)

    # print(raw_table)
    clean_ttt_table(raw_tables, pd.Series())



