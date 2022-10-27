import requests
import pandas as pd
import seaborn as sns
import numpy as np
import time, os
import datetime
import re
from datetime import date
from helpers.web_scraper import *
from helpers.export import export


def get_season_odds(season):
    url = 'https://oddspedia.com/us/basketball/usa/nba/odds'
    season_odds = get_odds_with_selenium(url, season)

    return season_odds


'''
def get_season_odds(season):
    season = str(int(season)-1) + '-' + season
    url = 'https://www.oddsportal.com/basketball/usa/nba-{}/results/'.format(season)
    season_odds = get_table_in_div(url, "tournamentTable")

    return get_page_html(url)
'''


def get_games():
    url = "https://www.basketball-reference.com/previews/"
    games = get_table(url, 'teams')
    #games = get_previews(url)
    return games

    # When scraping from ESPN website
    #url = 'https://www.espn.com/nba/schedule'
    #return get_schedule_table(url, 'schedule has-team-logos align-left')


def get_conference_standings(season, conference):
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_standings.html#all_confs_standings_E"
    
    if int(season) > 2015:
        # The tables in basketball reference are named confs_standings_E and confs_standings_W
        # Because of this, we only get the first letter of the input from the user in case they type "Eastern conference" for example
        standings = get_table(url, "confs_standings_" + conference[0].upper())
        return standings
    
    else:
        print("This only works for seasons 2016 and onward :-/")
        return ""


def get_division_Standings(season, conference):
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_standings.html#all_confs_standings_E"
    
    if int(season) <= 2015:
        # The tables in basketball reference are named confs_standings_E and confs_standings_W
        # Because of this, we only get the first letter of the input from the user in case they type "Eastern conference" for example
        standings = get_table(url, "division_standings_" + conference[0].upper())
        return standings
    
    else:
        print("This only works for seasons 2015 and earlier :-/")
        return ""


def get_expanded_standings(season):
    url = "https://www.basketball-reference.com/leagues/NBA_" + season + "_standings.html"
    standings = get_commented_table(url, 'expanded_standings')
    #standings.set_index('Team')
    return standings


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

    # Clean up the dataframe a bit
    monthly_results.columns = ["Date", 
            "Start (ET)", 
            "Away Team", 
            "Away Points", 
            "Home Team", 
            "Home Points", 
            "Score Type", 
            "OT?",
            "Attendence",
            "Arena",
            "Notes"]
 
    return monthly_results


def get_season_results(season, include_playoffs):
    # Get the season results
    results = get_monthly_results(season, "october")
    results = results.append(get_monthly_results(season, "november"), ignore_index=True)
    results = results.append(get_monthly_results(season, "december"), ignore_index=True)
    results = results.append(get_monthly_results(season, "january"), ignore_index=True)
    results = results.append(get_monthly_results(season, "february"), ignore_index=True)
    results = results.append(get_monthly_results(season, "march"), ignore_index=True)
    results = results.append(get_monthly_results(season, "april"), ignore_index=True)
    results = results.append(get_monthly_results(season, "may"), ignore_index=True)
    results = results.append(get_monthly_results(season, "june"), ignore_index=True)

    # Drop the playoff games if requested
    if include_playoffs == False:
        playoffs_start = results.loc[results["Date"] == "Playoffs"].index[0]
        results.drop(results.index[playoffs_start:], inplace=True)

    # Can't compare scores correctly when they're objects so we need to convert them
    results["Away Points"] = pd.to_numeric(results["Away Points"])
    results["Home Points"] = pd.to_numeric(results["Home Points"])

    return results


