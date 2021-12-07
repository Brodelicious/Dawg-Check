import requests
import json
import pandas

teams = {'GSW': 1610612744,
        'PHX':  1610612756,
        'BKN':  1610612751,
        'UTA':  1610612762,
        'CHI':  1610612741,
        'MIL':  1610612749,
        'WAS':  1610612764,
        'MIA':  1610612748,
        'MEM':  1610612763,
        'BOS':  1610612738,
        'CLE':  1610612739,
        'CHA':  1610612766,
        'PHI':  1610612755,
        'ATL':  1610612737,
        'LAC':  1610612746,
        'LAL':  1610612747,
        'DAL':  1610612742,
        'DEN':  1610612743,
        'MIN':  1610612750,
        'NYK':  1610612752,
        'POR':  1610612757,
        'TOR':  1610612761,
        'SAC':  1610612758,
        'SAS':  1610612759,
        'IND':  1610612754,
        'NOP':  1610612740,
        'HOU':  1610612745,
        'OKC':  1610612760,
        'ORL':  1610612753,
        'DET':  1610612765}



def teamroster():
    team = input("\nWhich team, bossman?\n")
    if team in teams:    
        teamID = teams.get(team)
        url = "https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=2021-22&TeamID=" + str(teamID)

        headers = {
            'sec-ch-ua': '"Opera GX";v="81", " Not;A Brand";v="99", "Chromium";v="95"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61',
            'Accept': 'application/json, text/plain, */*',
            'x-nba-stats-token': 'true',
            'Referer': 'https://www.nba.com/',
            'x-nba-stats-origin': 'stats',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = requests.request("GET", url, headers=headers, timeout=5)
        teamdata = response.json()

        df = pandas.json_normalize(teamdata['resultSets'])
        print(df.head())

        export(df, team + "_roster")
    else:
        print("Idk who that is...")
        userInput()



def export(df, name):
    yn = input("\nDo you want to save this data?\n")
    if yn == "yes" or yn == "y" or yn == "Yes" or yn == "Y":
        df.to_csv(name + '.csv', index = False)
        print("Data saved to file \"" + name + ".csv\"")
        userInput()
    if yn == "no" or yn == "n" or yn == "No" or yn == "N":
        userInput()
    else:
        print("Huh?\n")
        export(df, name)



def userInput():
    command = input("\nHow may I help you, mush?\n")
    if command == "team roster":
        teamroster()
    if command == "help":
        print("\nCommands:")
        print("\"team roster\" will return the roster for a team of your choice")
        userInput()
    else:
        print("what? (type \"help\" for a list of commands)")
        userInput()



print("\n~~~ Hello, mush. Welcome to the MUSH MASTER 3000 ~~~")
userInput()

