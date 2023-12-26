import numpy as np
import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.mlb_dao import *
from tabulate import tabulate
import sys

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

np.set_printoptions(threshold=sys.maxsize)

def modify_mlb_data():
    df = pd.DataFrame()
    for index, row in df.iterrows():
        # changes here
        print(df.iloc[row])
    return


def predict_mlb_games():
    predicted_column = 'Pitcher Runs'
    print('\nPredicting MLB Games...\n')
    df_2021 = pd.read_csv('data/CSVs/2021_season_data.csv')
    df_2022 = pd.read_csv('data/CSVs/2022_season_data.csv')
    df_2023 = pd.read_csv('data/CSVs/2023_season_data.csv')
    df = pd.concat([df_2021, df_2022, df_2023], ignore_index=True)

    # to do: shift season stats to adjust for them including the stats at the end of the game
    #x = df.drop(['Offense Runs', 'Date', 'Offense ID', 'Defense ID', 'Defense Pitcher ID', 'Offense Name', 'Defense Name', 'Defense Pitcher Name'], axis=1)
    df = df.drop(df[df['Pitcher Starts'] < 5].index)
    x = df[['Offense AVG', 'Offense OBP', 'Offense SLG', 'Pitcher ERA', 'Pitcher WHIP']]
    y = df[predicted_column]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=100)

    # Linear Regression Model
    lr = LinearRegression()
    lr.fit(x_train, y_train)

    y_lr_train_pred = lr.predict(x_train)
    y_lr_test_pred = lr.predict(x_test)

    lr_train_mse = mean_squared_error(y_train, y_lr_train_pred)
    lr_train_r2 = r2_score(y_train, y_lr_train_pred)
    lr_test_mse = mean_squared_error(y_test, y_lr_test_pred)
    lr_test_r2 = r2_score(y_test, y_lr_test_pred)

    lr_results = pd.DataFrame(['Linear Regression', lr_train_mse, lr_train_r2, lr_test_mse, lr_test_r2]).transpose()
    lr_results.columns = ['Method', 'Training MSE', 'Training R2', 'Test MSE', 'Test R2']

    # Random Forest Model
    rf = RandomForestRegressor(max_depth=2, random_state=100)
    rf.fit(x_train, y_train)

    y_rf_train_pred = rf.predict(x_train)
    y_rf_test_pred = rf.predict(x_test)

    rf_train_mse = mean_squared_error(y_train, y_rf_train_pred)
    rf_train_r2 = r2_score(y_train, y_rf_train_pred)
    rf_test_mse = mean_squared_error(y_test, y_rf_test_pred)
    rf_test_r2 = r2_score(y_test, y_rf_test_pred)

    rf_results = pd.DataFrame(['Random Forest', rf_train_mse, rf_train_r2, rf_test_mse, rf_test_r2]).transpose()
    rf_results.columns = ['Method', 'Training MSE', 'Training R2', 'Test MSE', 'Test R2']

    # Model results
    df_models = pd.concat([lr_results, rf_results], axis=0)
    print(tabulate(df_models, headers='keys', showindex=False))

    # Data visualization
    plt.figure(figsize=(5,5))
    plt.scatter(x=y_train, y=y_lr_train_pred, alpha=0.3)
    #z = np.polyfit(y_train, y_lr_train_pred, 1)
    #p = np.poly1d(z)
    #plt.plot(y_train, p(y_train))
    plt.xlabel('Actual Runs')
    plt.ylabel('Predicted Runs')
    #plt.show()

    # Predicting today's games
    #upcoming_games = get_upcoming_games()
    upcoming_games = get_stats_by_date_range('2023-08-01', '2023-08-01')
    predicted_games = upcoming_games[['Offense AVG', 'Offense OBP', 'Offense SLG', 'Pitcher ERA', 'Pitcher WHIP']]
    upcoming_games['Predicted Runs'] = lr.predict(predicted_games)
    print('\nPrediction of Upcoming Games:')
    print(tabulate(upcoming_games[['Offense Name', 'Offense AVG', 'Offense OBP', 'Offense SLG', 
                                   'Defense Name', 'Pitcher Name', 'Pitcher ERA', 'Pitcher WHIP', 
                                   predicted_column, 'Predicted Runs', 'Pitcher Innings']], 
                   headers='keys', showindex=False))

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
