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
        table = soup.find("table",{"class":table_name})

    else:
        print("\nSorry, boss. Couldn't find table with the given name\n")
        return

    headers = [th.getText() for th in table.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers

    rows = table.findAll('tr')[1:]
    data = [[td.getText() for td in rows[i].findAll(['td', 'th'])] for i in range(len(rows))]

    df = pd.DataFrame(data, columns = headers)

    return df


def get_commented_table(url, table_index):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    tables = []
    for each in comments:
        if 'table' in each:
            try:
                tables.append(pd.read_html(each)[0])
            except:
                continue

    return tables[table_index]

# For sports-reference.com game previews
def get_previews(url):
    #pd.options.display.max_columns = None
    pd.options.display.max_rows = None
    pd.options.display.width = None

    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="html.parser")

    previews = []
    for td in soup.find_all('td', class_= "right gamelink"):
        previews.append(td.find('a'))
        print(td)

    return previews


