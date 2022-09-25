import requests
import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export


def get_games():
    url = 'https://www.espn.com/nba/schedule'
    return get_schedule_table(url, 'schedule has-team-logos align-left')


def get_conference_standings(season, conference):
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_standings.html#all_confs_standings_E"
    
    if int(season) > 2015:
        # The tables in basketball reference are named confs_standings_E and confs_standings_W
        # Because of this, we only get the first letter of the input from the user in case they type "Eastern conference" for example
        standings = get_table(url, "confs_standings_" + conference[0].upper())
        return standings
    
    else:
        print("This only works for seasons 2016 and onward right now :-/")
        return ""


def get_per_game_stats(season):
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_per_game.html"
    per_game_stats = get_table(url, "per_game_stats")
    per_game_stats.head(10)
    return per_game_stats


def get_team_roster(team, season):
    url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
    return get_table(url, "roster")


def get_team_injuries(team, season):
    url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
    return get_commented_table(url, "injuries")


def get_team_per_game_stats(team, season):
    url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
    return get_table(url, "per_game")


def get_team_totals(team, season):
    url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
    return get_table(url, "totals")


def get_team_advanced_stats(team, season):
    url = "https://www.basketball-reference.com/teams/" + team + "/" + season + ".html"
    return get_table(url, "advanced")


def get_odds():
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

    return df


def get_season_summary_per_game_stats(season):
    url = 'https://www.basketball-reference.com/leagues/NBA_' + season + '.html'
    return get_table(url, 'per_game-team')


def get_monthly_results(season, month):
    url = 'https://www.basketball-reference.com/leagues/NBA_' + season + '_games-' + month + '.html'
    monthly_results = get_table(url, 'schedule')
    return monthly_results.rename(columns={"Home/Neutral": "Home", "Visitor/Neutral": "Away"})


