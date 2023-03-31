import requests
import pandas as pd
import seaborn as sns
import numpy as np
import time, os
import datetime
import re
#from datetime import date, datetime
from helpers.web_scraper import *
from helpers.convert import *


def get_season_spreads():
    season_spreads = scrape_season_odds('nba', 'spreads')
    return season_spreads


def get_season_props():
    season_spreads = scrape_season_odds('nba', 'props')
    return season_spreads


def get_upcoming_props():
    upcoming_props = scrape_upcoming_odds('nba', 'props')
    return upcoming_props


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

    # If we want to delete the playoffs row from the table
    monthly_results.drop(monthly_results[monthly_results['Date'] == 'Playoffs'].index, axis=0, inplace=True)
    # Convert the month
    monthly_results['Date'] = [convert_sports_reference_dates(date) for date in monthly_results['Date']]
    # Can't compare scores correctly when they're objects so we need to convert them
    monthly_results["Away Points"] = pd.to_numeric(monthly_results["Away Points"])
    monthly_results["Home Points"] = pd.to_numeric(monthly_results["Home Points"])

    return monthly_results


def get_current_season_results():
    # Some setup
    results = pd.DataFrame()
    date = datetime.date.today()
    if date.month == 10 or 11 or 12:
        season = str(date.year + 1)
    else:
        season = str(date.year)

    current_month = date.strftime('%B').lower()
    season_months = ['october', 
            'november', 
            'december', 
            'january', 
            'february', 
            'march', 
            'april', 
            'may', 
            'june']
    
    for month in season_months:
        if month == 'october':
            results = get_monthly_results(season, month)
        else:
            results = results.append(get_monthly_results(season, month), ignore_index=True)
        if current_month == month:
            break
        else:
            continue

    return results


def get_season_results(season):
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

    '''
    this stopped working so sportsreference.com might have changed their table
    # Drop the playoff games if requested
    if include_playoffs == False:
        playoffs_start = results.loc[results["Date"] == "Playoffs"].index[0]
        results.drop(results.index[playoffs_start:], inplace=True)
    '''

    return results


