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
import time
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
    odds_list = []

    # Get a list of the dates that need to be scraped
    date_range = pd.date_range(start=start_date, end=end_date)
    date_range = [d.strftime('%Y-%m-%d') for d in date_range]

    if 'player-props' in url:
        for date in date_range:
            date_odds = scrape_player_odds(url, driver, date)
            odds_list.extend(date_odds)

    else:
        for date in date_range:
            date_odds = scrape_game_odds(url, driver, date, draws)
            odds_list.extend(date_odds)

    driver.quit()
    if draws == 'yes':
        odds_df = pd.DataFrame(odds_list, columns=['Date', 'Game', 'Away Team', 'Away Odds', 'Home Team', 'Home Odds', 'Draw Odds'])
    else:
        odds_df = pd.DataFrame(odds_list, columns=['Date', 'Game', 'Away Team', 'Away Odds', 'Home Team', 'Home Odds'])
    return odds_df


def scrape_game_odds(url, driver, date, draws):
    wait = WebDriverWait(driver, 10)
    if '/?' in url:
        driver.get(url + '&date={}'.format(date))
    else:
        driver.get(url + '?date={}'.format(date))
    time.sleep(3)

    try:
        games_list = []
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

                # Create the row for the game and append it to the list of rows
                game_row = [date,
                              away_team + ' @ ' + home_team,
                              away_team,
                              away_open,
                              home_team,
                              home_open,
                              draw_open
                              ]
                # Append the scraped game to the list of games
                games_list.append(game_row)

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

                # Create the row for the game and append it to the list of rows
                game_row = [date,
                              away_team + ' @ ' + home_team,
                              away_team,
                              away_open,
                              home_team,
                              home_open
                              ]

                # Create the row for the game and append it to the list of rows
                games_list.append(game_row)

            else:
                # Draws variable is no bueno
                print('\n[Draws variable for {} is no bueno mi amigo]\n'.format(date))

        return games_list

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
