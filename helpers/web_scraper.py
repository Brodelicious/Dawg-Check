import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Comment
import requests
from requests.api import request


def get_table(url, table_name):
    #pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    if soup.find('table', id=table_name):
        table = soup.find('table', id=table_name)

    elif soup.find('table', id=table_name): 
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


