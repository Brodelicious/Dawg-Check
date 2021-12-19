import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen
import requests

def get_table(url, table_name):
    html = urlopen(url)
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find('table', id=table_name)

    headers = [th.getText() for th in table.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers[1:]

    rows = table.findAll('tr')[1:]
    data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

    df = pd.DataFrame(data, columns = headers)

    return df

def get_commented_table(url, table_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    comments = soup.find_all(string = lambda text: isinstance(text, Comment))

    tables = []
    for each in comments:
        if 'table' in each:
            try:
                print(each + "worked")
                tables.append(pd.read_html(each)[0])
            except:
                print(each + "didn't work")
                continue

    return tables
