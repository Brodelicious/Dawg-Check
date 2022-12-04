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


def get_bettingpros_odds(url):
    query = '?date=' + datetime.date(2022, 10, 19).strftime('%Y-%m-%d')
    bet_query = url + query
    base = datetime.datetime.today()
    delta = base - datetime.datetime(2022, 10, 19)
    date_list = [base - datetime.timedelta(days=x) for x in range(delta.days+1)]
    date_list = [d.strftime('%Y-%m-%d') for d in date_list]


    return


def get_oddspedia_spreads(url):
    # stuff I found online to make weird log messages leave me alone
    #options = Options()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Setup
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    # Navigate to the previous season
    driver.implicitly_wait(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div/div/main/div[1]/div[2]/button'))).click()
    driver.implicitly_wait(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/div[2]/div/div/main/div[1]/div[2]/div/div[2]'))).click()

    # Scrape the data for every game displayed on the page
    def scrape_page():
        print('\nWeek: {} / {}'.format())

        odds_data = {}
        driver.implicitly_wait(1)
        games = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'table-participant')))
        #games = driver.find_elements(By.CLASS_NAME, 'table-participant')
        print('games:')
        for game in games:
            print(game.text)

            print('... scraped')

        return odds_data

    # Loop through each week
    driver.implicitly_wait(1)
    week_dropdown_menu = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="match-odds"]/div[1]/div[1]/div[1]/button')))
    week_dropdown_menu.click()
    driver.implicitly_wait(3)
    weeks = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="match-odds"]/div[1]/div[1]/div[1]/div/*')))
    odds_data = {'Home', 'Away', 'Spread'}

    for week in weeks:
        # Click on the week
        print('about to click ' + week.text)
        driver.implicitly_wait(1)
        week.click()
        #print(week.text + ' scraped.')
        #odds_data.append(scrape_page())
        # Click the week dropdown again so the next week is clickable
        driver.implicitly_wait(3)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="match-odds"]/div[1]/div[1]/div[1]/button'))).click()
    
    # Pretty self explanatory
    print('Done scraping')
    driver.quit()

    # Create the dataframe to return
    headers = ['Home Team', 'Away Team', 'Spread']
    odds_dataframe = pd.DataFrame(odds_data, columns = headers)
    wait = WebDriverWait(driver, 10)

    return odds_dataframe


def get_oddsportal_odds(url, season):
    # stuff I found online to make weird log messages leave me alone
    #options = Options()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Setup
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Navigate to the correct season
    season_button_xpath = '//*[contains(text(), "{}")]'.format(season)
    season_button = driver.find_element(By.XPATH, season_button_xpath)
    season_button.click()

    # Click the accept cookie button or whatever
    # accept_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    accept_button = wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
    accept_button.click()

    # Scrape the data for every game displayed on the page
    final_page = int(driver.find_element(By.XPATH, '//*[@id="pagination"]/a[14]').get_attribute('x-page'))
    def scrape_page(current_page):
        print('\nPage: {} / {}'.format(current_page, final_page))
        odds_data = {}

        driver.implicitly_wait(1)
        games = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'table-participant')))
        #games = driver.find_elements(By.CLASS_NAME, 'table-participant')
        print('games:')
        for game in games:
            print(game.text)
            index = game.text.index('-')
            home_team = game.text[:index - 1]
            away_team = game.text[index + 1:]
            
            # in case I want to have multiple selenium instances getting games at the same time
            #game_link = game.find_element(By.XPATH, "//a").get_attribute('')
            game.click()
            driver.implicitly_wait(1)
            driver.find_element(By.XPATH, '//*[@id="bettype-tabs"]/ul/li[4]').click()
            driver.implicitly_wait(1)
            # Needs to find the spread with the closest odds
            table = driver.find_element(By.XPATH, '//*[id="odds-data-table"]')
            spreads = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'table-header-light')))
            #for spread in spreads:


        print('... scraped')

        # Go to the next page unless currently on the final page
        if(current_page == final_page):
            print('aight imma head out')
            return
        else:
            # To do: if there are less than 10 pages for some reason,
            # the xpath might not be a[13]. It might be useful to
            # find how many pageination buttons there are first
            next_page_xpath = '//*[@id="pagination"]/a[13]'
            #next_page_button = driver.find_element(By.XPATH, next_page_xpath)
            driver.implicitly_wait(1)
            next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, next_page_xpath)))
            next_page_button.click()
            current_page = current_page + 1
            scrape_page(current_page)

        return odds_data

    # Start by web scraping the first page
    odds_data = scrape_page(1)
    driver.quit()

    # Create the dataframe to return
    headers = ['Home Team', 'Away Team', 'Spread']
    odds_dataframe = pd.DataFrame(odds_data, columns = headers)
    wait = WebDriverWait(driver, 10)

    return odds_dataframe


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

