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
    team_id=get_team_id('Warriors'),
    player_id=get_player_id('Stephen', 'Curry'),
    context_measure_simple='PTS',
    season_nullable='2021-22',
    season_type_all_star='Regular Season')

# Load data into a Python dictionary
shot_data = json.loads(shot_json.get_json())

# Get the relevant data from our dictionary
relevant_data = shot_data['resultSets'][0]

# Get the headers and row data
headers = relevant_data['headers']
rows = relevant_data['rowSet']

# Create pandas DataFrame
curry_data = pd.DataFrame(rows)
curry_data.columns = headers

# Print the columns of our DataFrame
print(curry_data.columns)


# Creating a Basketball Court
# Function to draw basketball court
def create_court(ax, color):
    # Short corner 3PT lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)

    # 3PT Arc
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

    # Lane and Key
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

    # Rim
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))

    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)

    return ax


mpl.rcParams['font.family'] = 'futura'
mpl.rcParams['font.size'] = 14
mpl.rcParams['axes.linewidth'] = 2

# Create figure and axes
fig = plt.figure(figsize=(8, 7.52))
ax = fig.add_axes([0, 0, 1, 1])

# Plot hexbin of shots
ax.hexbin(curry_data['LOC_X'], curry_data['LOC_Y'] + 60, gridsize=(45, 45), extent=(-300, 300, 0, 940), bins='log',
          cmap='Blues')

# Draw court
ax = create_court(ax, 'black')

# Annotate player name and season
# ax.text(0, 1.05, 'Stephen Curry\n2021-22', transform=ax.transAxes, ha='left', va='baseline')

# Save and show figure
plt.savefig("NBA Shot Chart/ShotChart.png", dpi=72)
plt.show()

# write to csv file
curry_data.to_csv("NBA Shot Chart/Steph_Curry_21-22_R.csv", index=False)
