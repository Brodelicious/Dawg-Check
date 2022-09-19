import requests
import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.nba_dao import *


def nba_games():
    print("\nNBA Games Tonight:\n")

    print(get_nba_games())

    return


def nba_bets():
    print("\nHere's what we have cooking for the NBA tonight\n")

    url = 'https://www.espn.com/nba/schedule'
    games = get_nba_games()

    for i in range(len(games)):
        away_team = games.iloc[i]['Away Team']
        home_team = games.iloc[i]['Home Team']
        print("\n" + away_team + " @ " + home_team)
        print("Predicted outcome: ")
        print("Profitable bets: ")

    return


def nba_conference_standings():
    season = input("\nWhat season?\n")
    
    east_standings = get_nba_conference_standings(season, "confs_standings_E")
    west_standing = get_nba_conference_standings(season, "confs_standings_W")
    print()
    print(east_standings)
    print()
    print(west_standing)
    
    return


def nba_per_game_stats():
    season = input("\nWhat season?\n")

    print("\n" + season + " Per Game Stats:")
    per_game_stats = get_nba_per_game_stats(season)
    per_game_stats.head(10)
    print(per_game_stats)
    export(per_game_stats, str(date.today()) + "_per_game_stats")

    return


def nba_team_stats():
    team = input("\nWhich team, bossman?\n")
    season = input("\nWhat season?\n")

    print("\n" + team + " " + season + " TEAM STATS")

    print("\nRoster:")
    roster = get_nba_team_roster(team, season)
    print(roster)
    
    print("\nInjuries:")
    injuries = get_nba_team_injuries(team, season)
    print(injuries)

    print("\nPer Game:")
    per_game = get_nba_team_per_game_stats(team, season)
    print(per_game)

    print("\nTotals:")
    totals = get_nba_team_totals(team, season)
    print(totals)

    print("\nAdvanced:")
    advanced = get_nba_team_advanced_stats(team, season)
    print(advanced)

    #export(df, str(date.today()) + "_odds")
    return


def nba_odds():
    df = get_nba_odds()
    print(df)
    export(df, str(date.today()) + "_odds")

    return






