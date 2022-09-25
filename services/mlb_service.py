import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
from data.mlb_dao import *


def mlb_standings():
    print("\nSEASON STANDINGS: \n")

    print("\nAmerican League\n")
    print(get_al_central_standings())

    return


def mlb_games():
    print("\nMLB Games Today:\n")
    games = get_games()

    for game in games:
        print(game)
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
    batting_stats = get_table(url, "team_batting")
    print(batting_stats)

    print("\nPitching:")
    pitching_stats = get_table(url, "team_pitching")
    print(pitching_stats)

    #export(df, str(date.today()) + "_odds")
    return
