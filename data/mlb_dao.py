import pandas as pd
from helpers.web_scraper import *
import os
import requests
import datetime


# Used for previews of upcoming games (date is formated YYYY-MM-DD)
def get_scoreboard(date):
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

    games_list = []
    for game in data['games']:
        gamePk = int(game['gamePk'])
        date = str(date)
        away_team = game['teams']['away']['name']
        home_team = game['teams']['home']['name']
        try:
            away_pitcher = game['probablePitchers']['away']['fullName']
        except Exception as e:
            print('Exception caught: {} for {} @ {} on {}'.format(e, away_team, home_team, date))
            away_pitcher = '[UNKNOWN]'

        try:
            home_pitcher = game['probablePitchers']['home']['fullName']
        except Exception as e:
            print('Exception caught: {} for {} {}@{}'.format(e, date, away_team, home_team))
            home_pitcher = '[UNKNOWN]'

        games_list.append([
            gamePk,
            away_team + ' @ ' + home_team,
            date,
            away_team,
            away_pitcher,
            home_team,
            home_pitcher
            ])

    #games_df.set_index('gamePk')
    games_df = pd.DataFrame(games_list, columns=['gamePk', 'Game', 'Date', 'Away Team', 'Away Pitcher', 'Home Team', 'Home Pitcher'])
    return games_df


# Used when getting season box scores. Date format: YYY-MM-DD
def get_gamePks_by_date(date):
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

    games_list = []
    if 'games' in data:
        for game in data['games']:
            games_list.extend([game['gamePk']]) if games_list is not None else []

    return games_list


# Not working :(
def get_schedule(date):
    url = "https://baseballsavant.mlb.com/schedule?date=2023-7-4"  
    payload = {} 
    headers = {'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',   
               'Referer': 'https://baseballsavant.mlb.com/scoreboard',   
               'sec-ch-ua-mobile': '?0',   
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',   
               'sec-ch-ua-platform': '"Windows"' }  
    response = requests.request("GET", url, headers=headers, data=payload)  
    data = response.json()

    games_df = pd.DataFrame(columns=['gamePk', 'Date', 'Away Team', 'Away Pitcher', 'Home Team', 'Home Pitcher'])
    for game in data['schedule']['dates']['games']:
        gamePk = int(game['gamePk'])
        date = str(date)
        away_team = game['teams']['away']['team']['name']
        home_team = game['teams']['home']['team']['name']
        away_pitcher = game['teams']['away']['probablePitcher']['fullName']
        home_pitcher = game['teams']['home']['probablePitcher']['fullName']
        games_df = games_df._append({'gamePk':gamePk,
            'Date':date,
            'Away Team':away_team,
            'Away Pitcher':away_pitcher,
            'Home Team':home_team,
            'Home Pitcher':home_pitcher}, ignore_index=True)

    #games_df.set_index('gamePk')
    return games_df


# Used for results of finished games
# To do: make this use lists instead of appending a ton of dataframes
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
    box_score = []

    if position == 'pitching':
        for team in data['boxscore']['teams']:
            # Determine the starting pitcher IDs
            if team == 'away':
                try:
                    sp_id = data['away_pitcher_lineup'][0]
                    # May want to consider using the 'gamesStarted' stat but this seems to work all the same
                    gp = data['boxscore']['teams'][team]['players']['ID'+str(sp_id)]['stats']['pitching']['gamesPlayed']
                    if gp == 0:
                        sp_id = data['away_pitcher_lineup'][1]
                except IndexError: 
                    # Might not need the line assigning sp_id to 'NA' (need to determing if continue is enough to break the loop)
                    sp_id = ['NA']
                    continue
            else:
                try: 
                    sp_id = data['home_pitcher_lineup'][0]
                    # May want to consider using the 'gamesStarted' stat but this seems to work all the same
                    gp = data['boxscore']['teams'][team]['players']['ID'+str(sp_id)]['stats']['pitching']['gamesPlayed']
                    if gp == 0:
                        sp_id = data['away_pitcher_lineup'][1]
                except IndexError: 
                    # Might not need the line assigning sp_id to 'NA' (need to determing if continue is enough to break the loop)
                    sp_id = ['NA']
                    continue

            # Loop through the players until finding the starting pitcher stats
            for player in data['boxscore']['teams'][team]['players']:
                id = data['boxscore']['teams'][team]['players'][player]['person']['id']
                # Skip if they aren't the starting pitcher
                if id != sp_id:
                    continue
                date = data['gameDate']
                team_name = data['boxscore']['teams'][team]['team']['name']
                name = data['boxscore']['teams'][team]['players'][player]['person']['fullName']
                games_started = data['boxscore']['teams'][team]['players'][player]['seasonStats']['pitching']['gamesStarted']
                era = float(data['boxscore']['teams'][team]['players'][player]['seasonStats']['pitching']['era'])
                whip = float(data['boxscore']['teams'][team]['players'][player]['seasonStats']['pitching']['whip'])
                ip = float(data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['inningsPitched'])
                h = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['hits']
                r = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['runs']
                er = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['earnedRuns']
                bb = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['baseOnBalls']
                k = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['strikeOuts']
                hr = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['homeRuns']

                box_score_row=[
                    gamePk,
                    date,
                    team_name,
                    name,
                    id,
                    games_started,
                    era,
                    whip,
                    ip,
                    h,
                    r,
                    er,
                    bb,
                    k,
                    hr
                    ]
                box_score.append(box_score_row)

    if position == 'batting':
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

                box_score_row=[
                    gamePk,
                    date,
                    team_name,
                    name,
                    id,
                    position,
                    status,
                    ab,
                    r,
                    h,
                    rbi,
                    hr,
                    bb,
                    k,
                    lob,
                    tb,
                    rc,
                    avg,
                    obp,
                    slg,
                    ops
                    ]

                box_score.append(box_score_row)

    if position == 'team_batting':
        for team in data['boxscore']['teams']:
            date = data['gameDate']
            team_name = data['boxscore']['teams'][team]['team']['name']
            id = data['boxscore']['teams'][team]['team']['id']
            avg = float(data['boxscore']['teams'][team]['teamStats']['batting']['avg'])
            obp = float(data['boxscore']['teams'][team]['teamStats']['batting']['obp'])
            slg = float(data['boxscore']['teams'][team]['teamStats']['batting']['slg'])
            ops = float(data['boxscore']['teams'][team]['teamStats']['batting']['ops'])
            ab = data['boxscore']['teams'][team]['teamStats']['batting']['atBats']
            r = data['boxscore']['teams'][team]['teamStats']['batting']['runs']
            h = data['boxscore']['teams'][team]['teamStats']['batting']['hits']
            rbi = data['boxscore']['teams'][team]['teamStats']['batting']['rbi']
            hr = data['boxscore']['teams'][team]['teamStats']['batting']['homeRuns']
            bb = data['boxscore']['teams'][team]['teamStats']['batting']['baseOnBalls']
            k = data['boxscore']['teams'][team]['teamStats']['batting']['strikeOuts']
            lob = data['boxscore']['teams'][team]['teamStats']['batting']['leftOnBase']
            tb = data['boxscore']['teams'][team]['teamStats']['batting']['totalBases']
            #rc = (h+bb)*tb/(ab+bb)

            box_score_row=[
                gamePk,
                date,
                team_name,
                id,
                avg,
                obp,
                slg,
                ops,
                ab,
                r,
                h,
                rbi,
                hr,
                bb,
                k,
                lob,
                tb
                ]

            box_score.append(box_score_row)

    return box_score


def get_season_data(season):
    file_path = 'data/CSVs/{}_season_data.csv'.format(season)
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

    today = datetime.date.today()
    dates = {
            '2023': {'start': '2023-03-30', 'end': str(today - datetime.timedelta(days=1))},
            '2022': {'start': '2022-04-07', 'end': '2022-08-02'},
            '2021': {'start': '2021-04-01', 'end': '2021-08-03'},
            '2020': {'start': '2020-07-23', 'end': '2020-09-27'}
            }
    start_date = dates[season]['start']
    end_date = dates[season]['end']
    return get_data_by_date(start_date, end_date)
 

# Gets data used for predictive model
def get_data_by_date(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    date_range = [d.strftime('%#m/%#d/%Y') for d in date_range]

    # Setup
    pitching_cols = [
        'gamePk',
        'Date',
        'Team Name',
        'Name',
        'Id',
        'Games Started',
        'ERA',
        'WHIP',
        'IP',
        'H',
        'R',
        'ER',
        'BB',
        'K',
        'HR']
    batting_cols = [
        'gamePk',
        'Date',
        'Team Name',
        'Id',
        'AVG',
        'OBP',
        'SLG',
        'OPS',
        'AB',
        'R',
        'H',
        'RBI',
        'HR',
        'BB',
        'K',
        'LOB',
        'TB']
    game_cols = [
        'gamePk',
        'Date',
        'Team Name',
        'Team',
        'OBP',
        'SLG',
        'Opposing Pitcher',
        'ERA',
        'R']

    games_list = []
    for date in date_range:
        print('\nStarted scraping: ' + date)
        gamePks = get_gamePks_by_date(date)
        print('Games found: ' + ' '.join(gamePks))
        for gamePk in gamePks if gamePks is not None else []:
            # Collect team batting data
            batting_data = get_box_score(gamePk, 'team_batting')
            key_value_pairs = zip(batting_cols, batting_data[0])
            away_batting = dict(key_value_pairs)
            key_value_pairs = zip(batting_cols, batting_data[1])
            home_batting = dict(key_value_pairs)

            # Skip if the game was postponed to a later date
            # Note: if the code says it was moved to an earlier date than the original,
            # it was probably already started then paused to be resumed on the later date
            if date != away_batting['Date']:
                print('Skipping {} due to being moved from {} to {}'.format(gamePk, date, away_batting['Date']))
                continue

            # Collect pitching data
            pitching_data = get_box_score(gamePk, 'pitching')
            key_value_pairs = zip(pitching_cols, pitching_data[0])
            away_pitching = dict(key_value_pairs)
            key_value_pairs = zip(pitching_cols, pitching_data[1])
            home_pitching = dict(key_value_pairs)

            # To do: Collect odds data

            # Choose what data will be collected for each game
            game_data = [
                    [
                    gamePk,
                    date,
                    away_batting['Team Name'],
                    'Home',
                    away_batting['OBP'],
                    away_batting['SLG'],
                    home_pitching['Name'],
                    home_pitching['ERA'],
                    home_pitching['R']
                    ],
                    [
                    gamePk,
                    date,
                    home_batting['Team Name'],
                    'Away',
                    home_batting['OBP'],
                    home_batting['SLG'],
                    away_pitching['Name'],
                    away_pitching['ERA'],
                    away_pitching['R']
                    ]]

            print(game_data)
            games_list.extend(game_data)

    games_df = pd.DataFrame(games_list, columns=game_cols)
    return games_df
    

def get_box_scores_by_season(season, position):
    today = datetime.date.today()
    dates = {
            '2023': {'start': '2023-03-30', 'end': str(today - datetime.timedelta(days=1))},
            '2022': {'start': '2022-04-07', 'end': ''},
            '2021': {'start': '2021-04-01', 'end': ''},
            '2020': {'start': '2020-07-23', 'end': ''}
            }
    start_date = dates[season]['start']
    end_date = dates[season]['end']
    # Get a list of the dates that need to be scraped
    date_range = pd.date_range(start=start_date, end=end_date)
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]

    # Do the other stuff
    box_score_list = []
    for date in date_range:
        print('Started scraping: ' + date)
        games = get_gamePk_per_date(date)
        print(games)
        for game in games if games is not None else []:
            box_score_list.extend(get_box_score(game, position))

    if position == 'pitching':
        box_score_df = pd.DataFrame(box_score_list, columns=[
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
    elif position == 'batting':
        box_score_df = pd.DataFrame(box_score_list, columns=[
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
    elif position == 'team_batting':
        box_score_df = pd.DataFrame(box_score_list, columns=[
            'gamePk',
            'Date',
            'Team Name',
            'Name',
            'Id',
            'Position',
            'AB',
            'R',
            'H',
            'RBI',
            'HR',
            'BB',
            'K',
            'LOB',
            'TB',
            'AVG',
            'OBP',
            'SLG',
            'OPS'
            ])
    else:
        return None

    return box_score_df
    

def get_upcoming_odds(url, draws):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return scrape_odds(url, today, tomorrow, draws)


def get_upcoming_games():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    upcoming_games = pd.DataFrame(get_scoreboard(today))
    upcoming_games = upcoming_games._append(get_scoreboard(tomorrow), ignore_index=True)
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
