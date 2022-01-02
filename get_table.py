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
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
   
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        if comment.find(table_name) > 0:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            table = comment_soup.find("table")
        
            headers = [th.getText() for th in table.findAll('tr', limit=2)[0].findAll('th')]

            rows = table.findAll('tr')[1:]
            data = []

            for tr in rows:
                td = tr.find_all(['a', 'td'])
                row = []
                for tr in td:
                    if tr.text not in row:
                        row.append(tr.text)
                data.append(row)
                print(row)

            df = pd.DataFrame(data, columns = headers)

            return df
