from NBA import *


print("\n~~~ Hello, mush. Welcome to the MUSH MASTER 3000 ~~~")


def main():
    running = False

    command = input("\nHow may I help you, mush?\n")
    if command == "team roster" and running == False:
        running = True
        team_roster()
    if command == "odds" and running == False:
        running = True
        odds()
    if command == "per game stats" and running == False:
        running = True
        per_game_stats()
    if command == "team stats" and running == False:
        running = True
        team_stats()
    if command == "help" and running == False:
        print("\nCommands:")
        print("\"team roster\" will return the roster for a team of your choice")
        print("\"odds\" will return the odds data for today's games")
    else:
        if running == False:
            print("what? (type \"help\" for a list of commands)")
    main()


if __name__ == "__main__":
    main()
