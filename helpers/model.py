# Shout outs to this dude for the code.
# Wanted to type it out myself in a file here to learn before trying it myself.
# https://python.plainenglish.io/nba-betting-using-linear-regression-beba050a50fb

#%reset -fs
import pandas as pd
import seaborn as sns
import numpy as np
import requests
import time, os
from bs4 import BeautifulSoup
import datetime
import re
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', None)


chromedriver = '/Applications/chromedriver'
os.environ['webdriver.chrome/driver'] = chromedriver

#driver = webdriver.Chrome(chromedriver)
driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()))

# Set the base url
bet_search = 'https://www.bettingpros.com/nba/picks/prop-bets/bet/points/'
query = '?date=' + datetime.date(2021, 10, 19).strftime('%Y-%m-%d')
bet_query = bet_search + query

base = datetime.datetime.today()
delta = base - datetime.datetime(2021, 10, 19)
date_list = [base - datetime.timedelta(days=x) for x in range(delta.days+1)]
date_list = [d.strftime('%Y-%m-%d') for d in date_list]

bet_query = bet_search + '?date=' + '2021-12-20'
driver.get(bet_query)
soup = BeautifulSoup(driver.page_source, 'html.parser')

#run this initially; then don't run again if you just want to keep adding to it
final_df = pd.DataFrame()

# Gets data from each webpage by scraping the first 100 rows,
# checking if there was a next page button in the table,
# clicking if so, and scraping until there are no more pages
# in the table, then running itself again.
def get_data_rb():

    data_str = []
    data = []
    li = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table')
    date = soup.find('h1').text
    date = date.split(" ")[4]
    date.strip(')')
    date = date.replace('(',"").replace(')',"")
    house_accuracy = soup.find('div', class_='best-props__accuracy').text
    table_data = table.tbody.find_all('tr')
    for tr in table_data:
        data_str.append(tr.text.replace('\n', ' ').strip())
    for i in data_str:
        li = list(i.split('            '))
        data.append(li)
    for i in data:
        if len(i) == 7:
            i.append('TBD')
            i.append(date)
            i.append(house_accuracy)
        else:
            i.append(date)
            i.append(house_accuracy)
    global final_df
    final_df = final_df.append(pd.DataFrame(data))
    time.sleep(1)

    try:
        page_progress = driver.find_element_by_xpath('//div[contains(@class, "table__pagination")]').text.strip("<<").strip(">>").strip()
        if int(page_progress[5]) == int(page_progress[10]):
            return final_df
        else:
            element = driver.find_element_by_xpath('/html/body/div[2]/main/div/div/div/div[4]/div/div/a[2]')
            action = ActionChains(driver)
            action.move_to_element(element).click().perform()
            time.sleep(3)
            get_data_rb()
    except:
        return final_df


# This function navigates to the URL, clicks the accept cookie popup (if present)
# and then calls our get_data function
def get_site_rb(date):
    bet_query = bet_search + '?date=' + date
    driver.get(bet_query)
    time.sleep(5)
    try:
        element = driver.find_element_by_xpath('//*[id="onetrust-accept-btn-handler"]')
        action = ActionChains(driver)
        action.move_to_element(element).click().perform()
    except:
        pass
    get_data_rb()

# Run this then close the cookies pop-up
# Skips a couple dates where no games were played
for i in date_list:
    if i == '2021-12-24':
        continue
    if i == '2021-11-25':
        continue
    get_site_rb(i)

driver.close()

# Clean up below
final_df.columns=['Name', 'Team', 'Opp', 'Type', 'Line', 'Pick', 'Moneyline', 'Result', 'Date', 'Accuracy']

player_name = final_df.Name.str.split(" ", expand = True)
final_df['Name'] = player_name[2] + ' ' + player_name[4]

final_df.reset_index(inplace=True, drop=True)

final_df.drop(columns=['index'], inplace=True)

# Cleaning up the team and position info


print(final_df)
