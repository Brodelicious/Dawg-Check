from services.mlb_service import *
from services.nba_service import *
from helpers.export import export

# TO DO: add a dollar sign chain to the dawg
print('''\n Hello, Mush. Welcome to the...
  /$$$$$$$   /$$$$$$  /$$      /$$  /$$$$$$         /$$$$$$  /$$   /$$ /$$$$$$$$  /$$$$$$  /$$   /$$
 | $$__  $$ /$$__  $$| $$  /$ | $$ /$$__  $$       /$$__  $$| $$  | $$| $$_____/ /$$__  $$| $$  /$$/
 | $$  \ $$| $$  \ $$| $$ /$$$| $$| $$  \__/      | $$  \__/| $$  | $$| $$      | $$  \__/| $$ /$$/
 | $$  | $$| $$$$$$$$| $$/$$ $$ $$| $$ /$$$$      | $$      | $$$$$$$$| $$$$$   | $$      | $$$$$/
 | $$  | $$| $$__  $$| $$$$_  $$$$| $$|_  $$      | $$      | $$__  $$| $$__/   | $$      | $$  $$
 | $$  | $$| $$  | $$| $$$/ \  $$$| $$  \ $$      | $$    $$| $$  | $$| $$      | $$    $$| $$\  $$
 | $$$$$$$/| $$  | $$| $$/   \  $$|  $$$$$$/      |  $$$$$$/| $$  | $$| $$$$$$$$|  $$$$$$/| $$ \  $$
 |_______/ |__/  |__/|__/     \__/ \______/        \______/ |__/  |__/|________/ \______/ |__/  \__/
 ...experience

             ,--._______,-. 
           ,/,   ,    .  ,_`-. 
          / /  ,/ , _`  \. |  )       `-. . 
         (_/;````/ ```-._ ` \/ ______    \ \ 
           : ,o.-`- ,o.  )\` -`      `---.) ) 
           : , d8b ^-.   `|   `.      `    `. 
           |/ __:_     `. |  ,  `       `    \ 
           | ( ,-.`-.    ;`  ;   `       :    ; 
           | |  ,   `.      /     ;      :    \ 
           ;-``:::._,`.__),`             :     ; 
          / ,  `-   `--                  ;     | 
         /  \                   `       ,      | 
        (    `     :              :    ,\      | 
         \   `.    :     :        :  ,/  \    : 
          \    `|-- `     \ ,`    ,-`     :-.-`; 
          :     |`--.______;     |        :    : 
           :    /           |    |         |   \ 
           |    ;           ;    ;        /     ; 
         _/--` |   ~sup~   :`-- /         \_:_:_| 
       ,`,`,`  |           |___ \ 
       `^._,--`           / , , .) 
                          `-._,-` 
''')


def main():
    running = False

    command = input("\nHow may I help you?\n")

# MLB Commands
    if command == "mlb standings" and running == False:
        running = True
        mlb_standings()
        #export(games, str(date.today()) + "_odds")
    if command == "mlb team stats" and running == False:
        running = True
        mlb_team_stats()
        #export(games, str(date.today()) + "_odds")
    if command == "mlb games" and running == False:
        running = True
        mlb_games()
        #export(games, str(date.today()) + "_odds")
 
# NBA Commands
    if command == "predict nba spreads" and running == False:
        running = True
        nba_spread_predict()
    if command == "nba season props" and running == False:
        running = True
        nba_season_props()
    if command == "nba season spreads" and running == False:
        running = True
        nba_season_spreads()
    if command == "nba odds" and running == False:
        running = True
        nba_odds()
    if command == "nba conference standings" and running == False:
        running = True
        nba_conference_standings()
    if command == "nba per game stats" and running == False:
        running = True
        nba_per_game_stats()
    if command == "nba team stats" and running == False:
        running = True
        nba_team_stats()
    if command == "nba games" and running == False:
        running = True
        games = nba_games()
        export(games, str(date.today()) + "_games")
    if command == "nba bets" and running == False:
        running = True
        nba_bets()
    if command == "nba monthly results" and running == False:
        running = True
        nba_get_monthly_results()
    if command == "nba season results" and running == False:
        running = True
        nba_get_season_results()
    if command == "nba upcoming props" and running == False:
        running = True
        nba_upcoming_props()

# Other Commands
    if command == "help" and running == False:
        print("\nCommands:")
        print("\"nba team stats\" will return the stats for a team of your choice")
        print("\"nba odds\" will return the odds data for today's games")
        print("\"nba games\" will show today's NBA games")
    if command == "exit" and running == False:
        running = True
        return
    else:
        if running == False:
            print("what? (type \"help\" for a list of commands)")
    main()


if __name__ == "__main__":
    main()
