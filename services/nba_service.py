import pandas as pd
import numpy as np
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.nba_dao import *
from sklearn.metrics import f1_score, make_scorer, classification_report
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import scale
from sklearn.svm import SVC
from tabulate import tabulate
from collections import defaultdict
from IPython.display import display
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
#import xgboost as xgb


# Much of this code was based off of or taken from this presentation:
# https://www.youtube.com/watch?v=k7hSD_-gWMw&t=312s
def nba_predict():
    # Get the results for the season
    season = input("\nWhich season?\n")
    results = get_season_results(season, False)

    # This is our scoring mechanism. f1_score uses both wins and loses
    scorer = make_scorer(f1_score, pos_label=None, average='weighted')

    # Add the Home Win column
    results["Home Win"] = results["Away Points"] < results["Home Points"]

    # Our "class values".
    # This just keeps track of when the home team won to compare against our predicted wins
    y_true = results["Home Win"].values

    # Calculating home team win percentage
    n_games = results['Home Win'].count()
    n_home_wins = results['Home Win'].sum()
    win_percentage = n_home_wins / n_games
    print("\nHome win percentage: {0:.1f}%".format(100 * win_percentage))
    
    # F1 score rating for a model that assumes the home team will win every time.
    # This is the baseline score that we need to beat (at least)
    y_pred = [1] * len(y_true)
    print("F1: {:.4f}\n".format(f1_score(y_true, y_pred, pos_label=None, average='weighted')))

    # Compute the actual values for these
    # Did the home and away teams win their last game?
    # Add columns for showing if teams won their last game
    # Note: this is inneficient
    results["Home Last Win"] = False
    results["Away Last Win"] = False
    won_last = defaultdict(int)
    for index, row in results.iterrows():
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        row["Home Last Win"] = won_last[home_team]
        row["Away Last Win"] = won_last[away_team]
        results.iloc[index] = row
        #Set Current win
        won_last[home_team] = row["Home Win"]
        won_last[away_team] = not row["Home Win"]

    # Looks for a value and splits at that point (whether they won or lost their last game)
    # First create a data set
    x_previous_wins = results[["Home Last Win", "Away Last Win"]].values
    clf = DecisionTreeClassifier(random_state=14)
    scores = cross_val_score(clf, x_previous_wins, y_true, scoring=scorer)
    print("Using just the last result from the home and away teams")
    print("F1: {0:.4f}\n".format(np.mean(scores)))

    # Now we will extend this feature with win streaks
    results["Home Win Streak"] = 0
    results["Away Win Streak"] = 0
    # Did the home and away teams win their last game?
    win_streak = defaultdict(int)
    for index, row in results.iterrows(): # still inneficient
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        row["Home Win Streak"] = win_streak[home_team]
        row["Away Win Streak"] = win_streak[away_team]
        results.iloc[index] = row
        # Set current win
        if row["Home Win"]:
            win_streak[home_team] += 1
            win_streak[away_team] = 0
        else:
            win_streak[away_team] += 1
            win_streak[home_team] = 0
    print(tabulate(results.iloc[50:60][["Date", "Home Team", "Home Points", "Away Team", "Away Points", "Home Win", "Home Win Streak", "Away Win Streak"]], headers='keys'))
    # Predictions using the win streaks
    clf = DecisionTreeClassifier(random_state=14)
    x_win_streak = results[["Home Last Win", "Away Last Win", "Home Win Streak", "Away Win Streak"]].values
    scores = cross_val_score(clf, x_win_streak, y_true, scoring=scorer)
    print("\nUsing whether the home team is ranked higher:")
    print("\nF1: {0:.4f}\n".format(np.mean(scores)))

    return


# https://www.youtube.com/watch?v=6tQhoUuQrOw&t=125s
def nba_predict_2():
    # Get the results for the season
    season = input("\nWhich season?\n")
    data = get_season_results(season, False)
    #display(data.head())

    # Add the Home Win column
    data["Home Win"] = data["Away Points"] < data["Home Points"]

    # What is the win rate for the home team?
    n_games = data.shape[0]
    n_features = data.shape[1] - 1
    n_home_wins = data["Home Win"].sum()
    home_win_rate = (float(n_home_wins) / n_games) * 100
    print(home_win_rate)

    # Cool scatter plot thing
    scatter_matrix(data[['Home Points', 'Away Points', 'Attendence']], figsize=(10,10))
    plt.show(block=True)
    
    # Separate into feature set and target variable
    # FTR = Full Time Result
    x_all = data.drop(['Home Win'],1)
    y_all = data['Home Win']

    # Standardizing the data

    return


def nba_games():
    print("\nNBA Games Tonight:\n")

    print(get_games())

    return


def nba_bets():
    print("\nHere's what we have cooking for the NBA tonight\n")

    url = 'https://www.espn.com/nba/schedule'
    games = get_games()

    for i in range(len(games)):
        away_team = games.iloc[i]['Away Team']
        home_team = games.iloc[i]['Home Team']
        print("\n" + away_team + " @ " + home_team)
        print("Predicted outcome: ")
        print("Profitable bets: ")

    return


def nba_conference_standings():
    season = input("\nWhat season?\n")
    
    east_standings = get_conference_standings(season, "confs_standings_E")
    west_standing = get_conference_standings(season, "confs_standings_W")
    print()
    print(east_standings)
    print()
    print(west_standing)
    
    return


def nba_per_game_stats():
    season = input("\nWhat season?\n")

    print("\n" + season + " Per Game Stats:")

    per_game_stats = get_per_game_stats(season)
    per_game_stats.head(10)

    print(per_game_stats)

    export(per_game_stats, str(date.today()) + "_per_game_stats")

    return


def nba_get_monthly_results():
    season = input("\nWhat season?\n")
    month = input("\nWhich month?\n")

    monthly_results = get_monthly_results(season, month)

    print("\n" + month + " " + season + " Results:")
    print(tabulate(monthly_results, headers='keys'))

    export(monthly_results, "NBA_" +  month + "_" + season + "_results")

    return


def nba_get_season_results():
    # Get the season results
    season = input("\nWhat season?\n")
    include_playoffs = input("\nDo you want to include the playoff games? (y/n)")
    if include_playoffs == "y":
        include_playoffs = True
    elif include_playoffs == "n":
        include_playoffs = False
    else:
        "Try again Brodie"
    results = get_season_results(season, include_playoffs)

    print("\n" + season + " Results:")
    print(tabulate(results, headers='keys'))

    export(results, "NBA_" +  season + "_results")

    return


def nba_team_stats():
    team = input("\nWhich team, bossman?\n")
    season = input("\nWhat season?\n")

    print("\n" + team + " " + season + " TEAM STATS")

    print("\nRoster:")
    roster = get_team_roster(team, season)
    print(roster)
    
    print("\nInjuries:")
    injuries = get_team_injuries(team, season)
    print(injuries)

    print("\nPer Game:")
    per_game = get_team_per_game_stats(team, season)
    print(per_game)

    print("\nTotals:")
    totals = get_team_totals(team, season)
    print(totals)

    print("\nAdvanced:")
    advanced = get_team_advanced_stats(team, season)
    print(advanced)

    #export(df, str(date.today()) + "_odds")
    return


def nba_odds():
    df = get_odds()
    print(df)
    export(df, str(date.today()) + "_odds")

    return
