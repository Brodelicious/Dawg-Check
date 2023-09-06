import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.mlb_dao import *
from tabulate import tabulate


def predict_mlb_games():
    #train_df = pd.read_csv('data/CSVs/2022_season_data.csv')
    #test_df = pd.read_csv('data/CSVs/2023_season_data.csv')
    train_df = get_season_data('2022')
    test_df = get_season_data('2023')

    return


def download_mlb_season_data():
    season = input('What season would you like to download? ')

    season_data = get_season_data(season)
    export(season_data, '{}_season_data'.format(season))

    return


def mlb_upcoming_moneyline():
    url = 'https://www.bettingpros.com/mlb/odds/moneyline/'
    upcoming_games_df = get_upcoming_games()
    print("\nMLB Upcoming Games:")
    print(tabulate(upcoming_games_df, headers='keys'))

    upcoming_odds_df = get_upcoming_odds(url, 'no')
    print("\nMLB Upcoming Moneyline Odds:")
    print(tabulate(upcoming_odds_df, headers='keys'))

    return


def mlb_upcoming_f5():
    url = 'https://www.bettingpros.com/mlb/odds/moneyline/?prop=result-after-fifth-inning'
    upcoming_f5_df = get_upcoming_odds(url, 'yes')

    print("\nMLB Upcoming F5 Odds:")
    print(tabulate(upcoming_f5_df[['Date', 'Game', 'Away', 'Home', 'Draw']], headers='keys'))

    return


def mlb_season_moneyline():
    season = input("\nWhat season, bossman? (yyyy)\n")
    url = 'https://www.bettingpros.com/mlb/odds/moneyline/'
    season_f5_df = get_season_odds(url, season, 'f5', 'no')

    print("\nMLB First 5 Innings Season {} Results:\n".format(season))
    print(tabulate(season_f5_df[['Date', 'Game', 'Away', 'Home', 'Draw']], headers='keys'))
    export(season_f5_df, '2023_season_f5')

    return


def mlb_season_f5():
    season = input("\nWhat season, bossman? (yyyy)\n")
    url = 'https://www.bettingpros.com/mlb/odds/moneyline/?prop=result-after-fifth-inning'
    season_f5_df = get_season_odds(url, season, 'f5', 'yes')

    print("\nMLB First 5 Innings Season {} Results:\n".format(season))
    print(tabulate(season_f5_df[['Date', 'Game', 'Away', 'Home', 'Draw']], headers='keys'))
    export(season_f5_df, '2023_season_f5')

    return
