import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.mlb_dao import *
from tabulate import tabulate


def mlb_standings():
    print("\nSEASON STANDINGS: \n")

    print("\nAmerican League\n")
    print(get_al_central_standings())

    return


def mlb_upcoming_f5():
    upcoming_f5 = get_upcoming_f5()
    print("\nMLB Upcoming Games:")
    print(tabulate(upcoming_f5[['Date', 'Game', 'Away', 'Home', 'Draw']], headers='keys'))

    return


def mlb_season_f5():
    #season = input("\nWhat season, bossman? (yyyy/yyyy)\n")
    season_f5 = get_season_f5()
    print("\nMLB Season Spreads:\n")
    print(tabulate(season_f5[['Date', 'Game', 'Away', 'Home', 'Draw']], headers='keys'))
    export(season_f5, '2023_season_f5')

    return


def mlb_team_stats():
    team = input("\nWhich team, bossman?\n")
    season = input("\nWhat season?\n")

    print("\n" + team + " " + season + " TEAM STATS")

    print("\nBatting:")
    batting_stats = get_team_batting(team, season)
    #batting_stats = get_team_stats(team, season)[0]
    print(batting_stats)

    print("\nPitching:")
    pitching_stats = get_team_pitching(team, season)
    #pitching_stats = get_team_stats(team, season)[1]
    print(pitching_stats)

    #export(df, str(date.today()) + "_odds")
    return 


def mlb_team_stats2():
    team = input("\nWhich team, bossman?\n")
    season = input("\nWhat season?\n")
    url = "https://www.baseball-reference.com/teams/" + team + "/" + season + ".shtml"

    print("\n" + team + " " + season + " TEAM STATS")

    print("\nBatting:")
    batting_stats = get_(url, "team_batting")
    print(batting_stats)

    print("\nPitching:")
    pitching_stats = get_table(url, "team_pitching")
    print(pitching_stats)

    #export(df, str(date.today()) + "_odds")
    return
