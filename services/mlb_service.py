import numpy as np
import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.mlb_dao import *
from tabulate import tabulate

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder, LabelEncoder


def modify_mlb_data():
    df = pd.DataFrame()
    for index, row in df.iterrows():
        # changes here
        print(df.iloc[row])
    return


def predict_mlb_games():
    df_2021 = pd.read_csv('data/CSVs/2021_season_data.csv')
    df_2022 = pd.read_csv('data/CSVs/2022_season_data.csv')
    df_2023 = pd.read_csv('data/CSVs/2023_season_data.csv')
    df = pd.concat([df_2021, df_2022, df_2023], ignore_index=True)

    x = df.drop(['Offense Runs', 'Date', 'Offense ID', 'Defense ID', 'Defense Pitcher ID', 'Offense Name', 'Defense Name'], axis=1)
    y = df['Offense Runs']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=100)

    lr = LinearRegression()
    lr.fit(x_train, y_train)

    y_lr_train_pred = lr.predict(x_train)
    y_lr_test_pred = lr.predict(x_test)
    print(y_lr_train_pred, y_lr_test_pred)

    # to do: shift season stats to adjust for them including the stats at the end of the game
    return


def download_mlb_season_data():
    season = input('What season would you like to download? ')

    data = get_stats_by_season(season)
    export(data, '{}_season_data'.format(season))

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
