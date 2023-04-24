import pandas as pd
from datetime import date
from helpers.web_scraper import *
from helpers.export import export
import os
import requests


def get_schedule(date):
    url = "https://baseballsavant.mlb.com/scoreboard-data?date={}".format(date)
    headers = {
    'authority': 'baseballsavant.mlb.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'if-modified-since': 'Sun, 23 Apr 2023 21:24:17 GMT',
    'referer': 'https://baseballsavant.mlb.com/scoreboard',
    'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0'
    }
    response = requests.request("GET", url, headers=headers)
    data = response.json()

    games_df = pd.DataFrame(columns=['gamePk', 'Date', 'Away Team', 'Home Team'])
    for game in data['games']:
        gamePk = int(game['gamePk'])
        date = str(date)
        away_team = game['teams']['away']['name']
        home_team = game['teams']['home']['name']
        games_df = games_df.append({'gamePk':gamePk,
            'Date':date,
            'Away Team':away_team,
            'Home Team':home_team}, ignore_index=True)

    #games_df.set_index('gamePk')
    return games_df


def get_game_stats(gamePk):
    url = "https://baseballsavant.mlb.com/gf?game_pk={}".format(gamePk)
    payload = {}
    headers = {
    'authority': 'baseballsavant.mlb.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'referer': 'https://baseballsavant.mlb.com/gamefeed?date=4/23/2023&gamePk=718452&chartType=pitch&legendType=pitchName&playerType=pitcher&inning=&count=&pitchHand=&batSide=&descFilter=&ptFilter=&resultFilter=&hf=boxScore&sportId=1',
    'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    stats_df = pd.json_normalize(data)
    return stats_df


def get_upcoming_odds(url, draws):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return scrape_odds(url, today, tomorrow, draws)


def get_upcoming_games():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    upcoming_games = pd.DataFrame(get_schedule(today))
    upcoming_games = upcoming_games.append(get_schedule(tomorrow), ignore_index=True)
    return upcoming_games


def get_season_odds(url, season, bet_type, draws):
    file_path = 'data/CSVs/{}_season_{}.csv'.format(season, bet_type)
    today = datetime.date.today()
    
    # Check to see if data from this season has been scraped already
    if os.path.isfile(file_path):
        odds_df = pd.read_csv(file_path)
        last_date = odds_df.iloc[-1]['Date']
        start_date = datetime.datetime.strptime(last_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        print('\nFound CSV file. Last updated on: {}. Will check for spreads starting at {}'.format(last_date, start_date))
    else:
        odds_df = pd.DataFrame()
        start_date = datetime.date(season, 3, 30)
        print('\n[No existing file found at {}]'.format(file_path))

    # Check to see if we're scraping the current season
    if season == today.year:
        end_date = today - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(season, 10, 1)

    odds_df = odds_df.append(scrape_odds(url, start_date, end_date, draws))
    return odds_df


def get_season_box_scores(season, position):
    pitching_box_scores = pd.DataFrame()
    soup = get_page_html('https://www.baseball-reference.com/leagues/majors/{}-schedule.shtml'.format(season))
    games = soup.find_all('p', class_='game')
    print(soup)
    
    for game in games:
        elements = game.find_all('a')
        away_team = elements[0].text.replace(' ', '')
        home_team = elements[1].text.replace(' ', '')
        game_link = 'https://www.baseball-reference.com' + elements[2].get('href')
        print(game_link)
        print(away_team + position)
        pitching_box_scores = pitching_box_scores.append(get_table(game_link, away_team + position))
        pitching_box_scores = pitching_box_scores.append(get_table(game_link, home_team + position))
        
    return pitching_box_scores
