import pandas as pd
from helpers.web_scraper import *
from data.generic_dao import *
import os
import requests
import datetime

'''
Notes:
date format: YYYY-MM-DD
box score stats for the current game are included in season stat calculation when said game is finished
box score stats for the current game are not included in season stat calculation when said game is not finished (I think)
'''

stat_cols = [
    'Game ID',
    'Date',
    'Offense Name',
    'Offense ID',
    'Offense Games Played',
    'Offense Home Advantage',
    'Offense AVG',
    'Offense OBP',
    'Offense SLG',
    'Offense OPS',
    'Defense Name',
    'Defense ID',
    'Defense Games Played',
    'Defense Pitcher Name',
    'Defense Pitcher ID',
    'Defense Pitcher Starts',
    'Defense Pitcher ERA',
    'Defense Pitcher WHIP',
    'Offense Runs']


'''
stat_cols_old = [
    'gamePk',
    'Date',
    'Away Team Name',
    'Away Team ID',
    'Away Team Games Played',
    'Away Pitcher Name',
    'Away Pitcher ID',
    'Away Pitcher Starts',
    'Away Pitcher ERA',
    'Away Pitcher WHIP',
    'Away Team AVG',
    'Away Team OBP',
    'Away Team SLG',
    'Away Team OPS',
    'Away Team Runs',
    'Home Team Name',
    'Home Team ID',
    'Home Team Games Played',
    'Home Pitcher Name',
    'Home Pitcher ID',
    'Home Pitcher Starts',
    'Home Pitcher ERA',
    'Home Pitcher WHIP',
    'Home Team AVG',
    'Home Team OBP',
    'Home Team SLG',
    'Home Team OPS',
    'Home Team Runs',
    'Home Team Win']
'''


season_dates = {
    '2023': {'start': '2023-03-30', 'end': '2023-08-01'},
    '2022': {'start': '2022-04-07', 'end': '2022-08-02'},
    '2021': {'start': '2021-04-01', 'end': '2021-08-03'},
    '2020': {'start': '2020-07-23', 'end': '2020-09-27'}}

#==================== STAT SCRAPING ====================
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


def get_stats_by_season(season):
    file_path = 'data/CSVs/{}_season_data.csv'.format(season)
    if os.path.isfile(file_path):
        original_df = pd.read_csv(file_path)
        last_date = original_df.iloc[-1]['Date']
        start_date = datetime.datetime.strptime(last_date, '%m/%d/%Y') + datetime.timedelta(days=1)
        end_date = season_dates[season]['end']
        print('\nFound CSV file. Last updated on: {}. Will check for spreads starting at {}'.format(last_date, start_date))
        return original_df._append(get_stats_by_date_range(start_date, end_date))

    else:
        start_date = season_dates[season]['start']
        end_date = season_dates[season]['end']
        print('\n[No existing file found at {}]'.format(file_path))
        return get_stats_by_date_range(start_date, end_date)
 

def get_stats_by_date_range(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    date_range = [d.strftime('%#m/%#d/%Y') for d in date_range]
    stats_list = []
    for date in date_range:
        print('\nStarted scraping: ' + date)
        gamePks = get_gamePks_by_date(date)
        print('Games found: ' + ' '.join(gamePks))
        for gamePk in gamePks if gamePks is not None else []:
            game_stats = get_stats_by_game(gamePk)
            print(*game_stats, sep='\n')
            stats_list.extend(game_stats)

    games_df = pd.DataFrame(stats_list, columns=stat_cols)
    return games_df
    

def get_stats_by_game(gamePk):
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

    date = data['gameDate']
    # Away team stats
    away_team_name = data['boxscore']['teams']['away']['team']['name']
    away_team_id = data['boxscore']['teams']['away']['team']['id']
    away_games_played = data['away_team_data']['record']['gamesPlayed']
    away_sp_id = data['away_pitcher_lineup'][0]
    if data['boxscore']['teams']['away']['players']['ID'+str(away_sp_id)]['stats']['pitching']['gamesPlayed'] == 0:
        away_sp_id = data['away_pitcher_lineup'][1]
    for player in data['boxscore']['teams']['away']['players']:
        if away_sp_id == data['boxscore']['teams']['away']['players'][player]['person']['id']:
            away_pitcher_name = data['boxscore']['teams']['away']['players'][player]['person']['fullName']
            away_pitcher_id = data['boxscore']['teams']['away']['players'][player]['person']['id']
            away_pitcher_starts = data['boxscore']['teams']['away']['players'][player]['stats']['pitching']['gamesPlayed']
            away_pitcher_era = float(data['boxscore']['teams']['away']['players'][player]['seasonStats']['pitching']['era'])
            away_pitcher_whip = float(data['boxscore']['teams']['away']['players'][player]['seasonStats']['pitching']['whip'])
            break
    away_team_avg = float(data['boxscore']['teams']['away']['teamStats']['batting']['avg'])
    away_team_obp = float(data['boxscore']['teams']['away']['teamStats']['batting']['obp'])
    away_team_slg = float(data['boxscore']['teams']['away']['teamStats']['batting']['slg'])
    away_team_ops = float(data['boxscore']['teams']['away']['teamStats']['batting']['ops'])
    away_team_r = data['boxscore']['teams']['away']['teamStats']['batting']['runs']
    # Home team stats
    home_team_name = data['boxscore']['teams']['home']['team']['name']
    home_team_id = data['boxscore']['teams']['home']['team']['id']
    home_games_played = data['home_team_data']['record']['gamesPlayed']
    home_sp_id = data['home_pitcher_lineup'][0]
    if data['boxscore']['teams']['home']['players']['ID'+str(home_sp_id)]['stats']['pitching']['gamesPlayed'] == 0:
        home_sp_id = data['home_pitcher_lineup'][1]
    for player in data['boxscore']['teams']['home']['players']:
        if home_sp_id == data['boxscore']['teams']['home']['players'][player]['person']['id']:
            home_pitcher_name = data['boxscore']['teams']['home']['players'][player]['person']['fullName']
            home_pitcher_id = data['boxscore']['teams']['home']['players'][player]['person']['id']
            home_pitcher_starts = data['boxscore']['teams']['home']['players'][player]['stats']['pitching']['gamesPlayed']
            home_pitcher_era = float(data['boxscore']['teams']['home']['players'][player]['seasonStats']['pitching']['era'])
            home_pitcher_whip = float(data['boxscore']['teams']['home']['players'][player]['seasonStats']['pitching']['whip'])
            break
    home_team_avg = float(data['boxscore']['teams']['home']['teamStats']['batting']['avg'])
    home_team_obp = float(data['boxscore']['teams']['home']['teamStats']['batting']['obp'])
    home_team_slg = float(data['boxscore']['teams']['home']['teamStats']['batting']['slg'])
    home_team_ops = float(data['boxscore']['teams']['home']['teamStats']['batting']['ops'])
    home_team_r = data['boxscore']['teams']['home']['teamStats']['batting']['runs']

    stats = [
            [
            gamePk,
            date,
            away_team_name,
            away_team_id,
            away_games_played,
            False,
            away_team_avg,
            away_team_obp,
            away_team_slg,
            away_team_ops,
            home_team_name,
            home_team_id,
            home_games_played,
            home_pitcher_name,
            home_pitcher_id,
            home_pitcher_starts,
            home_pitcher_era,
            home_pitcher_whip,
            away_team_r
            ],
            [
            gamePk,
            date,
            home_team_name,
            home_team_id,
            home_games_played,
            True,
            home_team_avg,
            home_team_obp,
            home_team_slg,
            home_team_ops,
            away_team_name,
            away_team_id,
            away_games_played,
            away_pitcher_name,
            away_pitcher_id,
            away_pitcher_starts,
            away_pitcher_era,
            away_pitcher_whip,
            home_team_r
            ]
            ]

    return stats


'''
def get_stats_by_game_old(gamePk):
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

    date = data['gameDate']
    # Away team stats
    away_team_name = data['boxscore']['teams']['away']['team']['name']
    away_team_id = data['boxscore']['teams']['away']['team']['id']
    away_games_played = data['away_team_data']['record']['gamesPlayed']
    away_sp_id = data['away_pitcher_lineup'][0]
    if data['boxscore']['teams']['away']['players']['ID'+str(away_sp_id)]['stats']['pitching']['gamesPlayed'] == 0:
        away_sp_id = data['away_pitcher_lineup'][1]
    for player in data['boxscore']['teams']['away']['players']:
        if away_sp_id == data['boxscore']['teams']['away']['players'][player]['person']['id']:
            away_pitcher_name = data['boxscore']['teams']['away']['players'][player]['person']['fullName']
            away_pitcher_id = data['boxscore']['teams']['away']['players'][player]['person']['id']
            away_pitcher_starts = data['boxscore']['teams']['away']['players'][player]['stats']['pitching']['gamesPlayed']
            away_pitcher_era = float(data['boxscore']['teams']['away']['players'][player]['seasonStats']['pitching']['era'])
            away_pitcher_whip = float(data['boxscore']['teams']['away']['players'][player]['seasonStats']['pitching']['whip'])
            break
    away_team_avg = float(data['boxscore']['teams']['away']['teamStats']['batting']['avg'])
    away_team_obp = float(data['boxscore']['teams']['away']['teamStats']['batting']['obp'])
    away_team_slg = float(data['boxscore']['teams']['away']['teamStats']['batting']['slg'])
    away_team_ops = float(data['boxscore']['teams']['away']['teamStats']['batting']['ops'])
    away_team_r = data['boxscore']['teams']['away']['teamStats']['batting']['runs']
    # Home team stats
    home_team_name = data['boxscore']['teams']['home']['team']['name']
    home_team_id = data['boxscore']['teams']['home']['team']['id']
    home_games_played = data['home_team_data']['record']['gamesPlayed']
    home_sp_id = data['home_pitcher_lineup'][0]
    if data['boxscore']['teams']['home']['players']['ID'+str(home_sp_id)]['stats']['pitching']['gamesPlayed'] == 0:
        home_sp_id = data['home_pitcher_lineup'][1]
    for player in data['boxscore']['teams']['home']['players']:
        if home_sp_id == data['boxscore']['teams']['home']['players'][player]['person']['id']:
            home_pitcher_name = data['boxscore']['teams']['home']['players'][player]['person']['fullName']
            home_pitcher_id = data['boxscore']['teams']['home']['players'][player]['person']['id']
            home_pitcher_starts = data['boxscore']['teams']['home']['players'][player]['stats']['pitching']['gamesPlayed']
            home_pitcher_era = float(data['boxscore']['teams']['home']['players'][player]['seasonStats']['pitching']['era'])
            home_pitcher_whip = float(data['boxscore']['teams']['home']['players'][player]['seasonStats']['pitching']['whip'])
            break
    home_team_avg = float(data['boxscore']['teams']['home']['teamStats']['batting']['avg'])
    home_team_obp = float(data['boxscore']['teams']['home']['teamStats']['batting']['obp'])
    home_team_slg = float(data['boxscore']['teams']['home']['teamStats']['batting']['slg'])
    home_team_ops = float(data['boxscore']['teams']['home']['teamStats']['batting']['ops'])
    home_team_r = data['boxscore']['teams']['home']['teamStats']['batting']['runs']

    stats = [
            gamePk,
            date,
            away_team_name,
            away_team_id,
            away_games_played,
            away_pitcher_name,
            away_pitcher_id,
            away_pitcher_starts,
            away_pitcher_era,
            away_pitcher_whip,
            away_team_avg,
            away_team_obp,
            away_team_slg,
            away_team_ops,
            away_team_r,
            home_team_name,
            home_team_id,
            home_games_played,
            home_pitcher_name,
            home_pitcher_id,
            home_pitcher_starts,
            home_pitcher_era,
            home_pitcher_whip,
            home_team_avg,
            home_team_obp,
            home_team_slg,
            home_team_ops,
            home_team_r,
            int(home_team_r) > int(away_team_r)]

    return stats
'''


# (Currently unused)
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
                pitcher_id = data['boxscore']['teams'][team]['players'][player]['person']['id']
                # Skip if they aren't the starting pitcher
                if pitcher_id != sp_id:
                    continue
                date = data['gameDate']
                team_name = data['boxscore']['teams'][team]['team']['name']
                team_id = data['boxscore']['teams'][team]['team']['id']
                pitcher_name = data['boxscore']['teams'][team]['players'][player]['person']['fullName']
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
                hbp = data['boxscore']['teams'][team]['players'][player]['stats']['pitching']['hitByPitch']

                box_score_row=[
                    gamePk,
                    date,
                    team_name,
                    team_id,
                    pitcher_name,
                    pitcher_id,
                    games_started,
                    era,
                    whip,
                    ip,
                    h,
                    r,
                    er,
                    bb,
                    k,
                    hr,
                    hbp
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
                team_id = data['boxscore']['teams'][team]['team']['id']
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
                    team_id,
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
            team_id = data['boxscore']['teams'][team]['team']['id']
            if team == 'away':
                games_played = data['away_team_data']['record']['gamesPlayed']['team']['id']
            elif team == 'home':
                games_played = data['home_team_data']['record']['gamesPlayed']['team']['id']
            else:
                raise Exception ('Could not find games played')
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

            box_score_row=[
                gamePk,
                date,
                team_name,
                team_id,
                games_played,
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

    if position == 'team_pitching':
        for team in data['boxscore']['teams']:
            date = data['gameDate']
            team_name = data['boxscore']['teams'][team]['team']['name']
            team_id = data['boxscore']['teams'][team]['team']['id']
            era = float(data['boxscore']['teams'][team]['team']['teamStats']['pitching']['era'])
            whip = float(data['boxscore']['teams'][team]['team']['teamStats']['pitching']['whip'])
            h = data['boxscore']['teams'][team]['team']['teamStats']['pitching']['hits']
            r = data['boxscore']['teams'][team]['team']['teamStats']['pitching']['runs']
            er = data['boxscore']['teams'][team]['team']['teamStats']['pitching']['earnedRuns']
            bb = data['boxscore']['teams'][team]['team']['teamStats']['pitching']['baseOnBalls']
            k = data['boxscore']['teams'][team]['team']['teamStats']['pitching']['strikeOuts']
            hr = data['boxscore']['teams'][team]['team']['teamStats']['pitching']['homeRuns']

            box_score_row=[
                gamePk,
                date,
                team_name,
                team_id,
                era,
                whip,
                h,
                r,
                er,
                bb,
                k,
                hr
                ]
            box_score.append(box_score_row)

    return box_score


#==================== ODDS SCRAPING ====================
def get_upcoming_odds(url, draws):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return scrape_odds(url, today, tomorrow, draws)


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


#==================== PREVIEW SCRAPING ====================
def get_upcoming_games():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    upcoming_games = pd.DataFrame(get_scoreboard(today))
    upcoming_games = upcoming_games._append(get_scoreboard(tomorrow), ignore_index=True)
    return upcoming_games


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
