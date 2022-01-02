import requests
import pandas as pd
from datetime import date
from export import export
from get_table import *


teams = {'GSW': 1610612744,
        'PHX':  1610612756,
        'BKN':  1610612751,
        'UTA':  1610612762,
        'CHI':  1610612741,
        'MIL':  1610612749,
        'WAS':  1610612764,
        'MIA':  1610612748,
        'MEM':  1610612763,
        'BOS':  1610612738,
        'CLE':  1610612739,
        'CHA':  1610612766,
        'PHI':  1610612755,
        'ATL':  1610612737,
        'LAC':  1610612746,
        'LAL':  1610612747,
        'DAL':  1610612742,
        'DEN':  1610612743,
        'MIN':  1610612750,
        'NYK':  1610612752,
        'POR':  1610612757,
        'TOR':  1610612761,
        'SAC':  1610612758,
        'SAS':  1610612759,
        'IND':  1610612754,
        'NOP':  1610612740,
        'HOU':  1610612745,
        'OKC':  1610612760,
        'ORL':  1610612753,
        'DET':  1610612765}


def per_game_stats():
    season = input("\nWhat season?\n")
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_per_game.html"

    print("\n" + season + " Per Game Stats:")
    per_game_stats = get_table(url, "per_game_stats")
    per_game_stats.head(10)
    print(per_game_stats)
    export(per_game_stats, str(date.today()) + "_per_game_stats")

    return


def team_stats():
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
    print(per_game)

    print("\nAdvanced:")
    advanced = get_table(url, "advanced")
    print(advanced)

    #export(df, str(date.today()) + "_odds")
    return


def odds():
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


def team_roster():
    team = input("\nWhich team, bossman?\n")
    if team in teams:    
        teamID = teams.get(team)
        url = "https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=2021-22&TeamID=" + str(teamID)

        headers = {
            'sec-ch-ua': '"Opera GX";v="81", " Not;A Brand";v="99", "Chromium";v="95"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61',
            'Accept': 'application/json, text/plain, */*',
            'x-nba-stats-token': 'true',
            'Referer': 'https://www.nba.com/',
            'x-nba-stats-origin': 'stats',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = requests.request("GET", url, headers=headers, timeout=5)
        teamdata = response.json()

        df = pd.json_normalize(teamdata['resultSets'])
        print(df.head())

        export(df, team + "_roster")
    else:
        print("Idk who that is...")

    return

