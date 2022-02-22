# Source Code for JSON pull
# https://towardsdatascience.com/make-a-simple-nba-shot-chart-with-python-e5d70db45d0d


# Import packages
from nba_api.stats.endpoints import shotchartdetail
import json
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# Load Data
# Load teams file
teams = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json').text)

# Load players file
players = json.loads(requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json').text)


# Get team ID based on team name
def get_team_id(team_name):
    for team in teams:
        if team['simpleName'] == team_name:
            return team['teamId']
    return -1


# Get player ID based on player name
def get_player_id(first, last):
    for player in players:
        if player['firstName'] == first and player['lastName'] == last:
            return player['playerId']
    return -1

# Get the team ID number for the Lakers
lakers = get_team_id('Lakers')
print(lakers)

# Get the player ID number for Steph Curry
steph = get_player_id('Stephen', 'Curry')
print(steph)

# Create JSON request
shot_json = shotchartdetail.ShotChartDetail(
            team_id = get_team_id('Warriors'),
            player_id = get_player_id('Stephen', 'Curry'),
            context_measure_simple = 'PTS',
            season_nullable = '2021-22',
            season_type_all_star = 'Regular Season')
