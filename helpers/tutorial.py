import numpy as np
import pandas as pd
from datetime import date
from helpers.model import predict
from helpers.web_scraper import *
from helpers.export import export
from data.nba_dao import *
from tabulate import tabulate


# Much of this code was based off of or taken from this presentation:
# https://www.youtube.com/watch?v=k7hSD_-gWMw&t=312s
def nba_predict_tutorial():
    import numpy as np
    from sklearn.metrics import f1_score, make_scorer, classification_report
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    from sklearn.model_selection import GridSearchCV
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report
    from collections import defaultdict
    import seaborn as sns

    # Get the results for the season
    season = input("\nWhich season?\n")
    results = get_season_results(season)

    # This is our scoring mechanism. f1_score uses both wins and loses
    scorer = make_scorer(f1_score, pos_label=None, average='weighted')

    # Add the Home Win column
    results["Home Win"] = results["Away Points"] < results["Home Points"]

    # Our "class values".
    # This just keeps track of when the home team won to compare against our predicted wins
    y_true = results["Home Win"].values

    # Calculating home team win percentage
    n_games = results['Home Win'].count()
    n_home_wins = results['Home Win'].sum()
    win_percentage = n_home_wins / n_games
    print("\nHome win percentage: {0:.1f}%".format(100 * win_percentage))
    
    # F1 score rating for a model that assumes the home team will win every time.
    # This is the baseline score that we need to beat (at least)
    y_pred = [1] * len(y_true)
    print("F1: {:.4f}\n".format(f1_score(y_true, y_pred, pos_label=None, average='weighted')))

    # Compute the actual values for these
    # Did the home and away teams win their last game?
    # Add columns for showing if teams won their last game
    # Note: this is inneficient of setting these values
    results["Home Last Win"] = False
    results["Away Last Win"] = False
    won_last = defaultdict(int)
    for index, row in results.iterrows():
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        row["Home Last Win"] = won_last[home_team]
        row["Away Last Win"] = won_last[away_team]
        results.iloc[index] = row
        #Set Current win
        won_last[home_team] = row["Home Win"]
        won_last[away_team] = not row["Home Win"]

    # Looks for a value and splits at that point (whether they won or lost their last game)
    # First create a data set
    x_previous_wins = results[["Home Last Win", "Away Last Win"]].values
    clf = DecisionTreeClassifier(random_state=14)
    scores = cross_val_score(clf, x_previous_wins, y_true, scoring=scorer)
    print("Using just the last result from the home and away teams")
    print("F1: {0:.4f}\n".format(np.mean(scores)))

    # Now we will extend this feature with win streaks
    results["Home Win Streak"] = 0
    results["Away Win Streak"] = 0
    # Did the home and away teams win their last game?
    win_streak = defaultdict(int)
    for index, row in results.iterrows(): # still inneficient
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        row["Home Win Streak"] = win_streak[home_team]
        row["Away Win Streak"] = win_streak[away_team]
        results.iloc[index] = row
        # Set current win
        if row["Home Win"]:
            win_streak[home_team] += 1
            win_streak[away_team] = 0
        else:
            win_streak[away_team] += 1
            win_streak[home_team] = 0
    # Predictions using the win streaks
    clf = DecisionTreeClassifier(random_state=14)
    x_win_streak = results[["Home Last Win", "Away Last Win", "Home Win Streak", "Away Win Streak"]].values
    scores = cross_val_score(clf, x_win_streak, y_true, scoring=scorer)
    print("Using whether the home team has a higher win streak:")
    print("F1: {0:.4f}\n".format(np.mean(scores)))

    # Predictions using standings from the previous season
    standings = get_expanded_standings(str(int(season) - 1))
    standings.set_index('Team', inplace=True)
    #print("Previous season's standings:")
    #print(tabulate(standings, headers='keys'))

    def home_team_ranks_higher(row):
        home_team = row['Home Team']    
        away_team = row['Away Team']    
        # To do:
        # Make a dict of teams that have changed their names
        # so we don't have to hard code it here
        if season == '2014':
            if home_team == 'New Orleans Pelicans':
                home_team = 'New Orleans Hornets'
            if away_team == 'New Orleans Pelicans':
                away_team = 'New Orleans Hornets'
        if season == '2015':
            if home_team == 'Charlotte Hornets':
                home_team = 'Charlotte Bobcats'
            if away_team == 'Charlotte Hornets':
                away_team = 'Charlotte Bobcats'
        home_rank = standings.loc[home_team]['Rk']
        away_rank = standings.loc[away_team]['Rk']
        return home_rank < away_rank # Ranking higher means having a lower number

    # Applying the function allows us to avoid setting up a for loop and returns a series
    results['Home Team Ranks Higher'] = results.apply(home_team_ranks_higher, axis=1)
    #print(tabulate(results.iloc[:5][["Date", "Home Team", "Home Points", "Away Team", "Away Points", "Home Win", "Home Team Ranks Higher"]], headers='keys'))
    x_home_higher = results[["Home Last Win", "Away Last Win", "Home Team Ranks Higher"]].values
    clf = DecisionTreeClassifier(random_state=14)
    scores = cross_val_score(clf, x_home_higher, y_true, scoring=scorer)
    print("Using whether the home team ranked higher last season:")
    print("F1: {0:.4f}\n".format(np.mean(scores)))

    # Now we're going to try changing the parameters
    # We list all the parameters we want to try in the parameter_space
    # and GridSearchCV will try them will all different values.
    # For decision trees the different parameters don't matter as much though.
    # A support (or did he say sport?) vector machine works better with this
    parameter_space = {"max_depth": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20],}
    clf = DecisionTreeClassifier(random_state=14)
    grid = GridSearchCV(clf, parameter_space, scoring=scorer)
    grid.fit(x_home_higher, y_true)
    print("Using grid search to find the best parameter values:")
    print("F1: {0:.4f}\n".format(grid.best_score_))

    # Now we asses whether the home team won
    # the last time they played the away team
    last_game_winner = defaultdict(int)
    def home_team_won_last(row):
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        # Sort for a consistent ordering
        teams = tuple(sorted([home_team, away_team]))
        result = 1 if last_game_winner[teams] == row["Home Team"] else 0
        # Update the record for their next encounter
        winner = row["Home Team"] if row["Home Win"] else row["Away Team"]
        last_game_winner[teams] = winner
        return result
    results["Home Team Won Last"] = results.apply(home_team_won_last, axis=1)
    print(tabulate(results.iloc[90:100][["Date", "Home Team", "Home Points", "Away Team", "Away Points", "Home Win", "Home Team Won Last"]], headers='keys'))
    x_home_higher = results[["Home Last Win", "Away Last Win", "Home Team Ranks Higher", "Home Team Won Last"]].values
    clf = DecisionTreeClassifier(random_state=14)
    scores = cross_val_score(clf, x_home_higher, y_true, scoring=scorer)
    print("\nUsing whether the home team won their last game against the away team:")
    print("F1: {0:.4f}".format(np.mean(scores)))

    # Using a label encoder to assign a number to each team
    encoding = LabelEncoder()
    encoding.fit(results["Home Team"].values)
    home_teams = encoding.transform(results["Home Team"].values)
    away_teams = encoding.transform(results["Away Team"].values)
    x_teams = np.vstack([home_teams, away_teams]).T
    #print(x_teams[:5], x_teams.shape)
    # OneHotEncoder will take each feature (numbers assigned to teams)
    # and will create a new feature that will ask "Was the home team ______".
    # This turns a category into something that data mining algorithms can understand.
    onehot = OneHotEncoder()
    x_teams = np.asarray(onehot.fit_transform(x_teams).todense())
    print("\nHome:", x_teams[0,:30])
    print("Away:", x_teams[0,:30])
    clf = RandomForestClassifier(random_state=14)
    scores = cross_val_score(clf, x_teams, y_true, scoring=scorer)
    print("\nUsing full team labels and random forest classifier:")
    print("F1: {0:.4f}".format(np.mean(scores)))

    # Now we're going to try to improve the parameters
    parameter_space = {
                "max_features": [2, 10, 50, 'sqrt'],
                "n_estimators": [50, 100, 200],
                "criterion": ["gini", "entropy"],
                "min_samples_leaf": [1, 2, 4, 6],
            }
    clf = RandomForestClassifier(random_state=14)
    grid = GridSearchCV(clf, parameter_space, scoring=scorer)
    grid.fit(x_teams, y_true)
    print("\nAfter improving the parameter_space:")
    print("F1: {0:.4f}".format(grid.best_score_))
    print("Best parameters:", grid.best_estimator_)

    # Now we combine the team features with the other features
    x_all = np.hstack(([x_home_higher, x_teams]))
    print(x_all.shape)
    clf = DecisionTreeClassifier(random_state=14)
    scores = cross_val_score(clf, x_all, y_true, scoring=scorer)
    print("\nUsing team features combined with new parameters:")
    print("F1: {0:.4f}".format(np.mean(scores)))
    
    # Now we're going to try to improve the parameters with the combined features
    parameter_space = {
                "max_features": [2, 10, 50, 'sqrt'],
                "n_estimators": [50, 100, 200],
                "criterion": ["gini", "entropy"],
                "min_samples_leaf": [1, 2, 4, 6],
            }
    clf = RandomForestClassifier(random_state=14)
    grid = GridSearchCV(clf, parameter_space, scoring=scorer)
    grid.fit(x_all, y_true)
    print("\nAfter improving the parameter_space for the combined features:")
    print("F1: {0:.4f}".format(grid.best_score_))
    print("Best parameters:", grid.best_estimator_)

    # Graph time
    labels = ["Baseline", "Basic Features (DT)", "Teams (DT)", "Teams (RF)", "All (DT)", "All (RF - tuned)"]
    scores = [0.4261, 0.6028, 0.5967, 0.6049, 0.6034, 0.6384]
    sns.set(style="darkgrid", context="talk")
    sns.barplot(x=labels, y=scores);

    grid.fit(x_all, y_true)
    y_pred = grid.predict(x_all)
    print("\n")
    print(classification_report(y_true, y_pred))
    print("This results in getting {:.1f}% of predictions correct!".format(100*np.mean(y_pred == y_true)))

    return



