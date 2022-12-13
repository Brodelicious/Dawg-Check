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


def scrape_season_spreads(url, league):
    # stuff I found online to make weird log messages leave me alone
    #options = Options()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Setup
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    if(league == 'NBA'):
        start_date = datetime.date(2022, 10, 19)
    else:
        start_date = datetime
    today = datetime.date.today()

    query = '?date=' + datetime.date(2022, 10, 19).strftime('%Y-%m-%d')
    query = url + query
    base = datetime.datetime.today()
    delta = base - datetime.datetime(2022, 10, 19)
    date_list = [base - datetime.timedelta(days=x) for x in range(delta.days+1)]
    date_list = [d.strftime('%Y-%m-%d') for d in date_list]

    spread_df = pd.DataFrame()

    for date in date_list:
        driver.get('https://www.bettingpros.com/nba/odds/spread/?date=' + date)
        time.sleep(5)
        games = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'odds-offer')))
        for game in games:
            teams = game.find_elements(By.CLASS_NAME, 'team-overview__team-name')
            away_team = teams[0].text
            home_team = teams[1].text
            lines = game.find_elements(By.CLASS_NAME, 'odds-cell__line')
            odds = game.find_elements(By.CLASS_NAME, 'odds-cell__cost')
            away_line = lines[0].text
            away_odds = odds[0].text.strip('()')
            home_line = lines[1].text
            home_odds = odds[1].text.strip('()')

            game_df = pd.DataFrame({'Date':date,
                    'Away Team':away_team, 
                    'Away Line':away_line, 
                    'Away Odds':away_odds,
                    'Home Team':home_team, 
                    'Home Line':home_line, 
                    'Home Odds':home_odds}, index=[0])
            spread_df = spread_df.append(game_df, ignore_index=True)
        print(spread_df)

    driver.quit()
    return spread_df


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
        print("Sorry, boss. Couldn't find table with the name \'{}\'\n".format(table_name))
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

# For sports-reference.com game previews
def get_previews(url):
    #pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    previews = []
    for div in soup.find_all('div', class_= "game_summary nohover"):
        td = div.find('td', class_="right gamelink")
        previews.append(td.find('a'))

    return previews


def get_page_html(url):
    #pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    return soup

