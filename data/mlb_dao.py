import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export


def get_upcoming_f5():
    url = 'https://www.bettingpros.com/mlb/odds/moneyline/?prop=result-after-fifth-inning'
    return scrape_upcoming_odds(url)


def get_season_f5():
    url = 'https://www.bettingpros.com/mlb/odds/moneyline/?prop=result-after-fifth-inning'
    return scrape_season_odds('mlb', 'f5', url)


def get_al_central_standings():
    url = "https://www.baseball-reference.com/leagues/MLB-standings.shtml"
    al_central = get_table(url, "standings_c")
    return al_central


def get_team_stats(team, season):
    url = "https://www.baseball-reference.com/teams/" + team + "/" + season + ".shtml"
    batting_stats = get_table(url, "team_batting")
    pitching_stats = get_table(url, "team_pitching")
    return batting_stats, pitching_stats


def get_team_batting(team, season):
    url = "https://www.baseball-reference.com/teams/" + team + "/" + season + ".shtml"
    batting_stats = get_table(url, "team_batting")
    return batting_stats


def get_team_pitching(team, season):
    url = "https://www.baseball-reference.com/teams/" + team + "/" + season + ".shtml"
    pitching_stats = get_table(url, "team_pitching")
    return pitching_stats


def get_probable_pitchers():
    url = "https://www.baseball-reference.com/previews/"
    




