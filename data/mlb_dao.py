import pandas as pd
from helpers.web_scraper import *
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


def get_box_score(gamePk, position):
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
    box_score_df = []

    if position == 'pitching':
        box_score_df = pd.DataFrame(columns=[
            'gamePk',
            'Date',
            'Team Name',
            'Name',
            'Id',
            'Position',
            'Status',
            'IP',
            'H',
            'R',
            'ER',
            'BB',
            'K',
            'HR',
            'ERA',
            'WHIP'
            ])

        for team in data['boxscore']['teams']:
            for player in data['boxscore']['teams'][team]['players']:
                # Skip this player if they don't have batting stats
                if len(data['boxscore']['teams'][team]['players'][player]['stats']['pitching']) == 0:
                    continue
                date = data['gameDate']
                team_name = data['boxscore']['teams'][team]['team']['name']
                name = data['boxscore']['teams'][team]['players'][player]['person']['fullName']
                id = data['boxscore']['teams'][team]['players'][player]['person']['id']
                position = data['boxscore']['teams'][team]['players'][player]['position']['abbreviation']
                status = data['boxscore']['teams'][team]['players'][player]['status']['code']
                ip = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['atBats']
                h = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['hits']
                r = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['runs']
                er = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['rbi']
                bb = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['baseOnBalls']
                k = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['strikeOuts']
                hr = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['homeRuns']
                # If the era is missing it must be manually claculated
                try:
                    era = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['era']
                except Exception as e:
                    print('\nException caught: {} for {}:{}'.format(e, player, name))
                    era = (9*er)/ip
                    print('era manually calculated as (9 * {} er) / {} ip = {} era'.format(er, ip, era))
                # If the whip is missing it must be manually claculated
                try:
                    whip = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['whip']
                except Exception as e:
                    print('\nException caught: {} for {}:{}'.format(e, player, name))
                    whip = (bb+h)/ip
                    print('whip manually calculated as ({} bb + {} h) / {} ip = {} whip'.format(bb, h, ip, whip))

                box_score_row={
                    'gamePk':gamePk,
                    'Date':date,
                    'Team Name':team_name,
                    'Name':name,
                    'Id':id,
                    'Position':position,
                    'Status':status,
                    'IP':ip,
                    'H':h,
                    'R':r,
                    'ER':er,
                    'BB':bb,
                    'K':k,
                    'HR':hr,
                    'ERA':era,
                    'WHIP':whip
                    }

                box_score_df = box_score_df.append(box_score_row, ignore_index=True)

    if position == 'batting':
        box_score_df = pd.DataFrame(columns=[
            'gamePk',
            'Date',
            'Team Name',
            'Name',
            'Id',
            'Position',
            'Status',
            'AB',
            'R',
            'H',
            'RBI',
            'HR',
            'BB',
            'K',
            'LOB',
            'TB',
            'RC',
            'AVG',
            'OBP',
            'SLG',
            'OPS'
            ])

        for team in data['boxscore']['teams']:
            for player in data['boxscore']['teams'][team]['players']:
                # Skip this player if they don't have batting stats
                if len(data['boxscore']['teams'][team]['players'][player]['stats']['batting']) == 0:
                    continue
                date = data['gameDate']
                team_name = data['boxscore']['teams'][team]['team']['name']
                name = data['boxscore']['teams'][team]['players'][player]['person']['fullName']
                id = data['boxscore']['teams'][team]['players'][player]['person']['id']
                position = data['boxscore']['teams'][team]['players'][player]['position']['abbreviation']
                status = data['boxscore']['teams'][team]['players'][player]['status']['code']
                ab = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['atBats']
                r = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['runs']
                h = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['hits']
                rbi = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['rbi']
                hr = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['homeRuns']
                bb = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['baseOnBalls']
                k = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['strikeOuts']
                lob = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['leftOnBase']
                tb = data['boxscore']['teams'][team]['players'][player]['stats']['batting']['totalBases']
                rc = (h+bb)*tb/(ab+bb)
                avg = data['boxscore']['teams'][team]['players'][player]['seasonStats']['batting']['avg']
                obp = data['boxscore']['teams'][team]['players'][player]['seasonStats']['batting']['obp']
                slg = data['boxscore']['teams'][team]['players'][player]['seasonStats']['batting']['slg']
                ops = data['boxscore']['teams'][team]['players'][player]['seasonStats']['batting']['ops']

                box_score_row={
                    'gamePk':gamePk,
                    'Date':date,
                    'Team Name':team_name,
                    'Name':name,
                    'Id':id,
                    'Position':position,
                    'Status':status,
                    'AB':ab,
                    'R':r,
                    'H':h,
                    'RBI':rbi,
                    'HR':hr,
                    'BB':bb,
                    'K':k,
                    'LOB':lob,
                    'TB':tb,
                    'RC':rc,
                    'AVG':avg,
                    'OBP':obp,
                    'SLG':slg,
                    'OPS':ops
                    }

                box_score_df = box_score_df.append(box_score_row, ignore_index=True)

        if position == 'fielding':
            box_score_df = pd.DataFrame(columns=[
                'gamePk',
                'Date',
                'Team Name',
                'Name',
                'Id',
                'Position',
            'Status',
                ''
                ])

    return box_score_df


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
