import requests
from requests.sessions import Session

import pandas as pd

def start_webclient() -> Session:

    client = requests.session()
    client.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"})

    return client


def open_website_in_client(client:Session, url:str):
    result = client.get(url)
    print(result.status_code)
    print(f'Client request: {result.status_code}')

    table = pd.read_html(result.content.decode(result.encoding))[0]
    print(table.head())


def open_website_in_normal_get(url:str):
    headers = requests.utils.default_headers()
    headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"})
    result = requests.get(url, headers=headers)
    print(f'Default request: {result.status_code}')

    table = pd.read_html(result.content.decode(result.encoding))[0]
    print(table.head())


if __name__ == '__main__':

    client = start_webclient()
    url = 'https://nl.soccerway.com/national/netherlands/eredivisie/20222023/regular-season/r69885/tables/'
    open_website_in_client(client, url)
    open_website_in_normal_get(url)