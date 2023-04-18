import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
import os


def get_upcoming_odds(url, draws):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return scrape_odds(url, today, tomorrow, draws)


def get_season_odds(url, season, bet_type, draws):
    file_path = 'data/CSVs/{}_season_{}.csv'.format(season, bet_type)
    today = datetime.date.today()
    
    # Check to see if data from this season has been scraped already
    if os.path.isfile(file_path):
        spread_df = pd.read_csv(file_path)
        last_date = spread_df.iloc[-1]['Date']
        start_date = datetime.datetime.strptime(last_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        print('\nFound CSV file. Last updated on: {}. Will check for spreads starting at {}'.format(last_date, start_date))
    else:
        start_date = datetime.date(season, 3, 30)
        print('\n[No existing file found at {}]'.format(file_path))

    # Check to see if we're scraping the current season
    if season == today.year:
        end_date = today - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(season, 10, 1)

    return scrape_odds(url, start_date, end_date, draws)


def get_season_pitching_box_scores(season):
    pitching_box_scores = pd.DataFrame()
    soup = get_page_html('https://www.baseball-reference.com/leagues/majors/{}-schedule.shtml'.format(season))
    games = soup.find_all('a', text='Boxscore')
    
    for game in games:
        games = games.append(get_table(game.href, ''))
        
    return


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

