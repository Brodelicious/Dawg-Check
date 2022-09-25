import requests
import os
import pandas as pd
import numpy as np
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.nba_dao import *
from sklearn.metrics import f1_score, make_scorer, classification_report
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from tabulate import tabulate
from collections import defaultdict



# Much of this code was based off of or taken from this presentation:
# https://www.youtube.com/watch?v=k7hSD_-gWMw&t=312s
def nba_predict():
    # This is our scoring mechanism. f1_score uses both wins and loses
    scorer = make_scorer(f1_score, pos_label=None, average='weighted')

    # Get the season results
    season = input("\nWhat season?\n")
    results = get_monthly_results(season, "october")
    results = results.append(get_monthly_results(season, "november"))
    results = results.append(get_monthly_results(season, "december"))
    results = results.append(get_monthly_results(season, "january"))
    results = results.append(get_monthly_results(season, "february"))
    results = results.append(get_monthly_results(season, "march"))
    results = results.append(get_monthly_results(season, "april"))
    results = results.append(get_monthly_results(season, "may"))
    results = results.append(get_monthly_results(season, "june"))
    print(tabulate(results.iloc[:15], headers='keys'))

    # Clean up the dataframe a bit
    results.columns = ["Date", 
            "Start (ET)", 
            "Away Team", 
            "Away Points", 
            "Home Team", 
            "Home Points", 
            "Score Type", 
            "OT?",
            "Attend.",
            "Arena",
            "Notes"]
    results.drop(["Start (ET)", "Score Type", "OT?", "Attend.", "Arena", "Notes"], axis="columns", inplace=True)

    # Add the Home Win column
    results["Home Win"] = results["Home Points"] > results["Away Points"]

    # Our "class values"
    y_true = results["Home Win"].values

    n_games = results['Home Win'].count()
    n_home_wins = results['Home Win'].sum()
    win_percentage = n_home_wins / n_games

    print("\nHome win percentage: {0:.1f}%\n".format(100 * win_percentage))
    
    #y_pred = [1] * len(y_true)
    #print("F1: {:.4f}".format(f1_score((y_true, y_pred, pos_label=None, average='weighted'))))

    # Add columns for showing if teams won their last game
    '''
    results["Home Last Win"] = False
    results["Away Last Win"] = False
    won_last = defaultdict(int)
    for index, row in results.iterrows():
        home_team = row["Home"]
        away_team = row["Away"]
        row["Home Last Win"] = won_last[home_team]
        row["Away Last Win"] = won_last[away_team]
        results.loc[index] = row
        #Set Current win
        won_last[home_team] = row["Home Win"]
        won_last[away_team] = not row["Home Win"]
    '''

    # Get ranking
    clf = DecisionTreeClassifier(random_state=14)

    print(tabulate(results.iloc[:15], headers='keys'))


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






