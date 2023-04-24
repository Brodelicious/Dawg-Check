import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Comment
import requests
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.chrome.options import Options
import datetime
import time
import csv
import os
import logging


logger = logging.getLogger()


def scrape_odds(url, start_date, end_date, draws):
    # stuff I found online to make weird log messages leave me alone
    #options = Options()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Setup
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    final_df = pd.DataFrame()

    # Get a list of the dates that need to be scraped
    date_range = pd.date_range(start=start_date, end=end_date)
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]

    if 'player-props' in url:
        for date in date_range:
            date_df = scrape_player_odds(url, driver, date)
            final_df = final_df.append(date_df, ignore_index=True)

    else:
        for date in date_range:
            date_df = scrape_game_odds(url, driver, date, draws)
            final_df = final_df.append(date_df, ignore_index=True)

    driver.quit()
    return final_df


def scrape_game_odds(url, driver, date, draws):
    games_df = pd.DataFrame()
    wait = WebDriverWait(driver, 10)
    if '/?' in url:
        driver.get(url + '&date={}'.format(date))
    else:
        driver.get(url + '?date={}'.format(date))
    time.sleep(3)

    try:
        games = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'odds-offer')))
        for game in games:
            teams = game.find_elements(By.CLASS_NAME, 'team-overview__team-name')
            away_team = teams[0].get_attribute('href').split('/')[5].replace('-', ' ').title()
            if 'Ers' in away_team:
                away_team = away_team.replace('Ers', 'ers')
            home_team = teams[1].get_attribute('href').split('/')[5].replace('-', ' ').title()
            if 'Ers' in home_team:
                home_team = home_team.replace('Ers', 'ers')

            lines = game.find_elements(By.CLASS_NAME, 'odds-cell__line')

            # If we need to account for draws
            if draws == 'yes':
                # Get the opening lines/odds
                away_open = lines[0].text
                home_open = lines[1].text
                draw_open = lines[2].text
            
                # Get the best lines/odds
                away_best = lines[3].text
                home_best = lines[4].text
                draw_best = lines[5].text

                # Get the consensus lines/odds
                away_consensus = lines[-3].text
                home_consensus = lines[-2].text
                draw_consensus = lines[-1].text

                # Create the dataframe for the game and append it to the main dataframe
                game_df = pd.DataFrame({
                    'Date':date,
                    'Game':away_team + ' @ ' + home_team,
                    'Away Team':away_team, 
                    'Home Team':home_team, 
                    'Away':away_consensus, 
                    'Home':home_consensus, 
                    'Draw':draw_consensus
                    }, index=[0])

                # Append the scraped game to the games dataframe
                games_df = games_df.append(game_df, ignore_index=True)

            elif draws == 'no':
                # Get the opening lines/odds
                away_open = lines[0].text
                home_open = lines[1].text
            
                # Get the best lines/odds
                away_best = lines[2].text
                home_best = lines[3].text

                # Get the consensus lines/odds
                away_consensus = lines[-2].text
                home_consensus = lines[-1].text

                # Create the dataframe for the game and append it to the main dataframe
                game_df = pd.DataFrame({
                    'Date':date,
                    'Game':away_team + ' @ ' + home_team,
                    'Away Team':away_team, 
                    'Home Team':home_team, 
                    'Away':away_consensus, 
                    'Home':home_consensus
                    }, index=[0])

                # Append the scraped game to the games dataframe
                games_df = games_df.append(game_df, ignore_index=True)

            else:
                # Draws variable is no bueno
                print('\n[Draws variable for {} is no bueno mi amigo]\n'.format(date))

        return games_df

    except Exception as e:
        logger.exception('\n[EXCEPTION FOUND ON {}] \n{}'.format(date, str(e)))
        return


def scrape_player_odds(league, driver, date):
    props_df = pd.DataFrame()
    league = league.lower()
    url = 'https://www.bettingpros.com/{}/odds/player-props/points'.format(league)
    wait = WebDriverWait(driver, 30)
    driver.get(url + '/?date=' + date)
    time.sleep(5)
    try:
        props = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'odds-offer')))
        for prop in props:
            player = prop.find_element(By.CLASS_NAME, 'odds-player__heading').text
            lines = prop.find_elements(By.CLASS_NAME, 'odds-cell__line')

            # Create the dataframe for the game and append it to the main dataframe
            prop_df = pd.DataFrame({'Date':date,
                    'Player':player, 
                    'Line':lines[-1].text.split()[1]}, index=[0])

            props_df = props_df.append(prop_df, ignore_index=True)

        return props_df

    except Exception as e:
        logger.exception('\n[EXCEPTION FOUND ON {}] \n{}'.format(date, str(e)))
        return


def get_table(url, table_name):
    #pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    if soup.find('table', id=table_name):
        table = soup.find('table', id=table_name)

    elif soup.find('table', class_=table_name): 
        table = soup.find('table', class_=table_name)
        #table = soup.find("table",{"class":table_name})

    else:
        print("\nSorry, boss. Couldn't find the table you were looking for.")
        print('URL: {}\nTable Name: {}'.format(url, table_name))
        return

    headers = [th.getText() for th in table.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers

    rows = table.findAll('tr')[1:]
    data = [[td.getText() for td in rows[i].findAll(['td', 'th'])] for i in range(len(rows))]

    df = pd.DataFrame(data, columns = headers)

    return df


def get_table_in_div(url, div_name):
    #pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    # First find the div
    if soup.find('div', id=div_name):
        div = soup.find('table', id=div_name)

    elif soup.find('div', class_=div_name): 
        div = soup.find('table', class_=div_name)
        #table = soup.find("table",{"class":table_name})

    else:
        print("Sorry, boss. Couldn't find div with the name \'{}\'\n".format(div_name))
        return

    # Then find the table within the div
    if div.find('table'):
        table = soup.find('table', id=table_name)

    else:
        print("Sorry, boss. We found the div but couldn't find the table.\n")
        return

    headers = [th.getText() for th in table.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers

    rows = table.findAll('tr')[1:]
    data = [[td.getText() for td in rows[i].findAll(['td', 'th'])] for i in range(len(rows))]

    df = pd.DataFrame(data, columns = headers)

    return df


def get_commented_table(url, table_name):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    '''
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        if comment.find(table_name) > 0:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            table = comment_soup.find('table')

            headers = [th.getText() for th in table.find_all('tr', limit=2)[0].find_all('th')]
            rows = table.find_all('tr')[1:]
            data = []
            for tr in rows:
                td = tr.find_all(['a', 'td'])
                row=[]
                for tr in td:
                    if tr.text not in row:
                        row.append(tr.text)
                data.append(row)

            return pd.DataFrame(data, columns = headers)
    '''
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for each in comments:
        if each.find(table_name) > 0:
            try:
                # To Do:
                # The header=[1] is because the expanded standings table has two header rows.
                # Right now, this function is only used to grab the expanded standings table
                # but if we wanted to use this for other tables we should find another way
                # to drop that row from the nba_dao get_expanded_standings() method instead.
                return pd.read_html(each, header=[1])[0]
            except:
                continue

    return 


def get_page_html(url):
    #pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    return soup


'''
def scrape_season_odds(league, bet_type, url):
    # stuff I found online to make weird log messages leave me alone
    #options = Options()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Setup
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    final_df = pd.DataFrame()
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    if today.month in [10, 11, 12]:
        season = str(today.year + 1)
    else:
        season = str(today.year)

    # TO DO: fix the year to not be hard coded
    if(league == 'nba'):
        start_date = datetime.date(2022, 10, 19)
    if(league == 'mlb'):
        start_date = datetime.date(2023, 3, 30)
    else:
        start_date = datetime.date(2022, 10, 19)

    # Check to see if data from this season has been scraped already
    file_path = 'data/CSVs/{}_season_{}.csv'.format(season, bet_type)
    if os.path.isfile(file_path):
        spread_df = pd.read_csv(file_path)
        last_date = spread_df.iloc[-1]['Date']
        start_date = datetime.datetime.strptime(last_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        print('\nFound CSV file. Last updated on: {}. Will check for spreads starting at {}'.format(last_date, start_date))
    else:
        print('\n[No existing file found at {}]'.format(file_path))

    # Get a list of the dates that need to be scraped
    date_range = pd.date_range(start=start_date, end=yesterday)
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]

    if 'player-props' in url:
        for date in date_range:
            #url = 'https://www.bettingpros.com/{}/odds/{}/prop={}/?date={}'.format(league, bet_type, prop, date)
            date_df = scrape_games(url, driver, date)
            final_df = final_df.append(date_df, ignore_index=True)

    else:
        for date in date_range:
            date_df = scrape_games(url, driver, date)
            final_df = final_df.append(date_df, ignore_index=True)

    driver.quit()
    return final_df


def scrape_upcoming_odds(url):
    # stuff I found online to make weird log messages leave me alone
    #options = Options()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Setup
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    final_df = pd.DataFrame()
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    date_range = pd.date_range(start=today, end=tomorrow)
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]

    if 'player-props' in url:
        for date in date_range:
            #url = 'https://www.bettingpros.com/{}/odds/{}/prop={}/?date={}'.format(league, bet_type, prop, date)
            date_df = scrape_games(url, driver, date)
            final_df = final_df.append(date_df, ignore_index=True)

    else:
        for date in date_range:
            try:
                date_df = scrape_games(url, driver, date)
                final_df = final_df.append(date_df, ignore_index=True)
            except Exception as e:
                # this usually means bookies haven't put out odds for tomorrow
                logger.exception('\n[EXCEPTION FOUND ON {}] \n{}'.format(date, str(e)))

    driver.quit()
    return final_df

def scrape_spreads(league, driver, date):
    spreads_df = pd.DataFrame()
    league = league.lower()
    url = 'https://www.bettingpros.com/{}/odds/spread'.format(league)
    wait = WebDriverWait(driver, 10)
    driver.get(url + '/?date=' + date)
    time.sleep(3)

    try:
        games = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'odds-offer')))
        for game in games:
            teams = game.find_elements(By.CLASS_NAME, 'team-overview__team-name')
            away_team = teams[0].get_attribute('href').split('/')[5].replace('-', ' ').title()
            if 'Ers' in away_team:
                away_team = away_team.replace('Ers', 'ers')
            home_team = teams[1].get_attribute('href').split('/')[5].replace('-', ' ').title()
            if 'Ers' in home_team:
                home_team = home_team.replace('Ers', 'ers')

            lines = game.find_elements(By.CLASS_NAME, 'odds-cell__line')
            odds = game.find_elements(By.CLASS_NAME, 'odds-cell__cost')

            # Get the opening lines/odds
            away_line_open = lines[0].text
            away_odds_open = odds[0].text.strip('()')
            home_line_open = lines[1].text
            home_odds_open = odds[1].text.strip('()')
            
            # Get the best lines/odds
            away_line_best = lines[2].text
            away_odds_best = odds[2].text.strip('()')
            home_line_best = lines[3].text
            home_odds_best = odds[3].text.strip('()')

            # Get the consensus lines/odds
            away_line_consensus = lines[-2].text
            away_odds_consensus = odds[-2].text.strip('()')
            home_line_consensus = lines[-1].text
            home_odds_consensus = odds[-1].text.strip('()')

            # Create the dataframe for the game and append it to the main dataframe
            game_df = pd.DataFrame({'Date':date,
                    'Away Team':away_team, 
                    'Away Line Open':away_line_open, 
                    'Away Odds Open':away_odds_open,
                    'Away Line':away_line_consensus, 
                    'Away Odds':away_odds_consensus,
                    'Away Line Best':away_line_best, 
                    'Away Odds Best':away_odds_best,
                    'Home Team':home_team, 
                    'Home Line Open':home_line_consensus, 
                    'Home Odds Open':home_odds_consensus,
                    'Home Line':home_line_consensus, 
                    'Home Odds':home_odds_consensus,
                    'Home Line Best':home_line_best, 
                    'Home Odds Best':home_odds_best}, index=[0])
            spreads_df = spreads_df.append(game_df, ignore_index=True)

        return spreads_df

    except Exception as e:
        logger.exception('\n[EXCEPTION FOUND ON {}] \n{}'.format(date, str(e)))
        return
'''
