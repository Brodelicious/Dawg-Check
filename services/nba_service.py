import numpy as np
import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.nba_dao import *
from tabulate import tabulate

def nba_predict():
    return

def nba_games():
    print("\nNBA Games Tonight:\n")
    print(get_games())

    return


def nba_season_odds():
    season = input("\nWhat season, bossman? (yy/yy)\n")
    season_odds = get_season_odds(season)

    print("\nNBA " + season + " Season Odds:\n")
    print(season_odds)

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
