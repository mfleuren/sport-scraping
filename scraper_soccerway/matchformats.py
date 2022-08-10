from urllib import request
import webscraper
import pandas as pd
import importlib
import requests

importlib.reload(webscraper)


def create_clubs_url(year:int, competition:str) -> str:
    return f'https://nl.soccerway.com/national/netherlands/eredivisie/{year}/regular-season/{competition}/tables/'





if __name__ == '__main__':


    url = create_clubs_url(20222023, 'r69885')
    webscraper.extract_clubs_from_html(url)