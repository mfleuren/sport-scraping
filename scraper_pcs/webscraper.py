import requests
import pandas as pd
from unidecode import unidecode

def scrape_website(web_url: str) -> pd.DataFrame:
    """Scrape all information from a website, return as a string."""

    result = requests.get(web_url)
    statuscode = result.status_code

    if statuscode == 200:
        result_table = read_result_table(result.text)

    else:
        print(f'Website {url} could not be accessed; status code {statuscode}')

    return result_table


def read_result_table(html_text: str) -> pd.DataFrame:
    """Read the results from the table found in HTML input"""
    table_list = pd.read_html(html_text)

    print(table_list[0].head())
    results_table = clean_results_table(table_list[0])

    return results_table


def clean_results_table(raw_table: pd.DataFrame) -> pd.DataFrame:
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
    results_table['FIRSTNAME'] = results_table.apply(lambda x: x['RIDER'].replace(x['SURNAME'], ''), axis=1)
   
    return results_table


if __name__ == '__main__':
    url = 'https://www.procyclingstats.com/race/volta-ao-algarve/2022/stage-2'
    standings = ['', '-gc', '-points', '-kom', '-youth']

    for url_epi in standings:
        outcome = scrape_website(url + url_epi)
        print(outcome.head())

