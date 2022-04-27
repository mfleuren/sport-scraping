
import requests
import pandas as pd
from unidecode import unidecode
from datetime import datetime
from utility.dataclasses import StageResults

PCS_BASE_URL = 'https://www.procyclingstats.com/race/'
PCS_YEAR = str(datetime.now().year)
PCS_BASE_EPITHET = 'result'


def construct_pcs_url(epithet: str) -> str:
    """Construct the URL for PCS based on defaults and match-specific epithet."""
    url = PCS_BASE_URL + epithet + '/' + PCS_YEAR + '/' + PCS_BASE_EPITHET
    return url


def scrape_website(results: StageResults, match: pd.Series) -> StageResults:
    """Scrape all information from a website, return as a string."""

    url = construct_pcs_url(match['URL_EPITHET'])
    result = requests.get(url)
    statuscode = result.status_code

    if statuscode == 200:
        result_table = read_result_table(result.text, match)
    else:
        print(f'Website {url} could not be accessed; status code {statuscode}')

    results.stage_results.append(result_table)

    return results


def read_result_table(html_text: str, match: pd.Series) -> pd.DataFrame:
    """Read the results from the table found in HTML input"""
    table_list = pd.read_html(html_text)
    results_table = clean_results_table(table_list[0], match)

    return results_table


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

    # Add match information
    results_table['MATCH'] = match['MATCH']
    results_table['MATCH_LEVEL'] = match['LEVEL']

    # Drop unnecessary columns
    results_table.rename({'Team':'TEAM', 'Age':'AGE', 'Rnk':'RNK'}, axis=1, inplace=True)

    COLUMNS_TO_KEEP = ['RNK', 'RIDER', 'FIRSTNAME', 'SURNAME', 'TEAM', 'MATCH', 'MATCH_LEVEL']
   
    return results_table[COLUMNS_TO_KEEP]


if __name__ == '__main__':
    url = 'https://www.procyclingstats.com/race/volta-ao-algarve/2022/stage-2'
    standings = ['', '-gc', '-points', '-kom', '-youth']

    for url_epi in standings:
        outcome = scrape_website(url + url_epi)
        print(outcome.head())

