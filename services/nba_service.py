import requests
import pandas as pd
from datetime import date
from helpers.get_table import *
from helpers.export import export
from data.nba_dao import *


def nba_games():
    print("\nNBA Games Tonight:\n")

    print(get_nba_games())

    return


def nba_bets():
    print("\nHere's what we have cooking for the NBA tonight\n")

    url = 'https://www.espn.com/nba/schedule'
    games = get_schedule_table(url, 'schedule has-team-logos align-left')

    url = "https://www.basketball-reference.com/leagues/NBA_" + "2022" + "_standings.html#all_confs_standings_E"

    for i in range(len(games)):
        away_team = games.iloc[i]['Away Team']
        home_team = games.iloc[i]['Home Team']
        print("\n" + away_team + " @ " + home_team)
        print("Predicted outcome: ")
        print("Profitable bets:")

    return


def nba_conference_standings():
    season = input("\nWhat season?\n")
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_standings.html#all_confs_standings_E"
    
    if int(season) > 2015:
        east_standings = get_table(url, "confs_standings_E")
        west_standing = get_table(url, "confs_standings_W")
        print()
        print(east_standings)
        print()
        print(west_standing)
    
    else:
        print("This only works for seasons 2016 and onward right now :-/")

    return


def nba_per_game_stats():
    season = input("\nWhat season?\n")
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_per_game.html"

    print("\n" + season + " Per Game Stats:")
    per_game_stats = get_table(url, "per_game_stats")
    per_game_stats.head(10)
    print(per_game_stats)
    export(per_game_stats, str(date.today()) + "_per_game_stats")

    return


def nba_team_stats():
    team = input("\nWhich team, bossman?\n")
    season = input("\nWhat season?\n")
    url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"

    print("\n" + team + " " + season + " TEAM STATS")

    print("\nRoster:")
    roster = get_table(url, "roster")
    print(roster)
    
    print("\nInjuries:")
    injuries = get_commented_table(url, "injuries")
    print(injuries)

    print("\nPer Game:")
    per_game = get_table(url, "per_game")
    print(per_game)

    print("\nTotals:")
    totals = get_table(url, "totals")
    print(totals)

    print("\nAdvanced:")
    advanced = get_table(url, "advanced")
    print(advanced)

    #export(df, str(date.today()) + "_odds")
    return


def nba_odds():
    url = "https://cdn.nba.com/static/json/liveData/odds/odds_todaysGames.json"
    headers = {
        'authority': 'cdn.nba.com',
	'sec-ch-ua': '"Opera GX";v="81", " Not;A Brand";v="99", "Chromium";v="95"',
	'sec-ch-ua-mobile': '?0',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61',
 	'sec-ch-ua-platform': '"Windows"',
 	'accept': '*/*',
	'origin': 'https://www.nba.com',
 	'sec-fetch-site': 'same-site',
 	'sec-fetch-mode': 'cors',
 	'sec-fetch-dest': 'empty',
 	'referer': 'https://www.nba.com/',
 	'accept-language': 'en-US,en;q=0.9',
	'if-none-match': '"862f8896ec0a96bec826bc1db1fd7d20"',
	'if-modified-since': 'Tue, 07 Dec 2021 17:58:42 GMT',
    }

    response = requests.request("GET", url, headers=headers)
    oddsdata = response.json()
    df = pd.json_normalize(oddsdata)
    print(df)
    export(df, str(date.today()) + "_odds")

    return
