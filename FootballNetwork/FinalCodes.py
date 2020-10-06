import urllib.request, json 
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import seaborn as sns
import functools
import seaborn as sns; sns.set(color_codes=True)

## Creating a dataset for each macth ##

with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/8658.json") as url:
    croatia_france = json.loads(url.read().decode())
croatia_france = json_normalize(croatia_france, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/8652.json") as url:
    croatia_russia = json.loads(url.read().decode())
croatia_russia = json_normalize(croatia_russia, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/8656.json") as url:
    croatia_england = json.loads(url.read().decode())
croatia_england = json_normalize(croatia_england, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7581.json") as url:
    croatia_denmark = json.loads(url.read().decode())
croatia_denmark = json_normalize(croatia_denmark, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7545.json") as url:
    data = json.loads(url.read().decode())
croatia_argentina = json_normalize(data, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7529.json") as url:
    croatia_nigeria = json.loads(url.read().decode())
croatia_nigeria = json_normalize(croatia_nigeria, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7561.json") as url:
    croatia_iceland = json.loads(url.read().decode())
croatia_iceland = json_normalize(croatia_iceland, sep = "_")

# Merging all games into one DataFrame #
croatia_all = pd.concat([croatia_argentina, croatia_denmark,croatia_england,
           croatia_france, croatia_nigeria, croatia_russia, croatia_iceland], join = 'outer', sort = False)

#  events that is not related to Croatia #
croatia_all = croatia_all[(croatia_all['team_name'] == 'Croatia')]

## Preparing for network analysis ##

# Use only events where Croatia is in possession of the ball #
croatia_all = croatia_all[(croatia_all['possession_team_name'] == 'Croatia')]

# Finding the Player IDs and its corresponding player name
croatia_playerID = croatia_all[['player_id', 'player_name']]
croatia_playerID = croatia_playerID.groupby('player_id', as_index = False).agg({'player_name':'unique'})

# Converting into excel in order to create the nodes table #
croatia_playerID.to_excel('nodes.xlsx')

# Create subset with only passes-info and pass receiver info #
croatia_passes = croatia_all[['pass_recipient_id', 'player_id']]
croatia_passes = croatia_passes.dropna(axis = 0)

# Converting into excel in order to create the edges table
croatia_passes.to_excel('edges.xlsx')


### Creating the Football field ###

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle, ConnectionPatch
import seaborn as sns

def draw_pitch(ax):
    # size of the pitch is 120, 80
    #Create figure

    #Pitch Outline & Centre Line
    plt.plot([0,0],[0,80], color="grey")
    plt.plot([0,120],[80,80], color="grey")
    plt.plot([120,120],[80,0], color="grey")
    plt.plot([120,0],[0,0], color="grey")
    plt.plot([60,60],[0,80], color="grey")

    #Left Penalty Area
    plt.plot([14.6,14.6],[57.8,22.2],color="grey")
    plt.plot([0,14.6],[57.8,57.8],color="grey")
    plt.plot([0,14.6],[22.2,22.2],color="grey")

    #Right Penalty Area
    plt.plot([120,105.4],[57.8,57.8],color="grey")
    plt.plot([105.4,105.4],[57.8,22.5],color="grey")
    plt.plot([120, 105.4],[22.5,22.5],color="grey")

    #Left 6-yard Box
    plt.plot([0,4.9],[48,48],color="grey")
    plt.plot([4.9,4.9],[48,32],color="grey")
    plt.plot([0,4.9],[32,32],color="grey")

    #Right 6-yard Box
    plt.plot([120,115.1],[48,48],color="grey")
    plt.plot([115.1,115.1],[48,32],color="grey")
    plt.plot([120,115.1],[32,32],color="grey")

    #Prepare Circles
    centreCircle = plt.Circle((60,40),8.1,color="grey",fill=False)
    centreSpot = plt.Circle((60,40),0.71,color="grey")
    leftPenSpot = plt.Circle((9.7,40),0.71,color="grey")
    rightPenSpot = plt.Circle((110.3,40),0.71,color="grey")

    #Draw Circles
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)
    
    leftArc = Arc((9.7,40),height=16.2,width=16.2,angle=0,theta1=310,theta2=50,color="grey")
    rightArc = Arc((110.3,40),height=16.2,width=16.2,angle=0,theta1=130,theta2=230,color="grey")

    #Draw Arcs
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)
    
fig=plt.figure()
fig.set_size_inches(7, 5)
ax=fig.add_subplot(1,1,1)
draw_pitch(ax)

### Possession Heat Map ###
croatia_action = croatia_all['location']
croatia_action = croatia_action.dropna(axis = 0)
croatia_action = pd.DataFrame(croatia_action)
croatia_action = pd.DataFrame(croatia_all['location'].dropna(axis = 0))

Cmin = min(croatia_action['location'])
Cmax = max(croatia_action['location'])
my_cmap = sns.light_palette("Navy", as_cmap = True)

fig, ax = plt.subplots(1,1)
fig.set_size_inches(7, 5)
x_coord = [i[0] for i in croatia_action['location']]
y_coord = [i[1] for i in croatia_action['location']]
sns.kdeplot(x_coord,y_coord, shade = 'true', n_levels = 30,cmap = my_cmap)
sm = plt.cm.ScalarMappable(cmap=my_cmap)
sm._A = []
plt.colorbar(sm)
draw_pitch(ax)
plt.show()

### Network Analysis ###

import csv
import networkx as nx
from operator import itemgetter
import pandas as pd

with open('Nodes.csv', 'r') as nodecsv: # Open the file                       
    nodereader = csv.reader(nodecsv,delimiter=';') # Read the csv  
    # Retrieve the data (using Python list comprhension and list slicing to remove the header row, see footnote 3)
    nodes = [n for n in nodereader][1:]                     

node_names = [n[0] for n in nodes] # Get a list of only the node names 

with open('Edges.csv', 'r') as edgecsv: # Open the file
    edgereader = csv.reader(edgecsv,delimiter=';') # Read the csv     
    edges = [e for e in edgereader][1:] # Retrieve the data

with open('Kit_Numbers.csv', 'r') as kitcsv: # Open the file
    kitreader = csv.reader(kitcsv,delimiter=',') # Read the csv     
    kit = [f for f in kitreader] # Retrieve the data
    
## DATA CHECK ##
print(len(node_names))
print(len(edges))

##CREATE GRAPH##
G = nx.MultiDiGraph()

#G=nx.DiGraph()

G.add_nodes_from(node_names)
G.add_edges_from(edges)
print(nx.info(G))

## RENAME THE NODES ##
dict_nodes = dict(nodes)
nx.relabel_nodes(G,mapping = dict_nodes,copy=False)

## PLACE THE PLAYERS ON THE FIELD WITH POSITIONS ##
pos2 = {'Subasic':(3,41), 'Lovren':(15,30), 'Kovacic':(0,0), 'Strinic':(25,70), 'Pjaca':(0,0), 'Kramaric':(0,0), 'Vrsaljko':(25,10), 'Modric':(65,20), 'Rebic':(90,10), 'Vida':(15,50), 'Brozovic':(45,40), 'Rakitic':(65,60), 'Mandzukic':(100,40), 'Perisic':(90,70), 'Corluka':(0,0), 'Badelj':(0,0), 'Caleta-Car':(0,0), 'Pivaric':(0,0), 'Jedvaj':(0,0), 'Bradaric':(0,0), 'Kalinic':(0,0)}
nx.draw_networkx(G,pos=pos2)

## REMOVE NODES WHERE PLAYERS PLAYED LESS THAN 4 GAMES ##

G.remove_nodes_from(['Bradaric','Kramaric', 'Corluka', 'Jedvaj', 'Badelj', 'Pjaca', 'Kovacic', 'Kalinic',  'Caleta-Car','Pivaric'])

#d = G.degree()
#d = [(d[node]+1) * 1 for node in G.nodes()]

## DIFFERENT MEASUREMENTS ##
density = nx.density(G)
print("Network density:", density)

degree_dict = dict(G.degree(G.nodes()))
nx.set_node_attributes(G, degree_dict, 'degree')
sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True)

print("Top 20 nodes by degree:")
for d in sorted_degree[:20]:
    print(d)

betweenness_dict = nx.betweenness_centrality(G) # Run betweenness centrality
eigenvector_dict = nx.eigenvector_centrality_numpy(G) # Run eigenvector centrality
closeness_dict = nx.closeness_centrality(G)

# Assign each to an attribute in your network
nx.set_node_attributes(G, betweenness_dict, 'betweenness')
nx.set_node_attributes(G, eigenvector_dict, 'eigenvector')
nx.set_node_attributes(G, closeness_dict, 'closeness')

sorted_betweenness = sorted(betweenness_dict.items(), key=itemgetter(1), reverse=True)
sorted_eigenvector = sorted(eigenvector_dict.items(), key=itemgetter(1), reverse=True)
sorted_closeness = sorted(closeness_dict.items(), key=itemgetter(1), reverse=True)

print("Top 11 nodes by Betweenness centrality:")
for b in sorted_betweenness[:20]:
    print(b)


print("Top 11 nodes by Eigenvector Centrality:")
for b in sorted_eigenvector[:20]:
    print(b)
    
print("Top 11 nodes by Closeness Centrality:")
for b in sorted_closeness[:20]:
    print(b)

	node_color = dict(nx.betweenness_centrality(G))  
	node_color1 = dict(nx.eigenvector_centrality(G))  
	node_color2 = dict(nx.closeness_centrality(G))  
	node_color_degree = list(node_color.values())  
	node_color_degree  
	  
	vmin = min(node_color_degree)  
	vmax = max(node_color_degree)  
	  
	draw_pitch(ax)  
	nx.draw_networkx(G,pos=pos3, node_size = 2000, node_color=node_color_degree, cmap=plt.cm.Reds)  
	sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin = vmin, vmax=vmax))  
	sm._A = []  
	plt.text(x = 150,y = 55,s = ' 2 Vrsalkjo \n 3 Strinic \n 4 Perisic \n 6 Lovren \n 7 Rakitic \n 10 Modric \n 11 Brozovic \n 17 Mandzukic \n 18 Rebic \n 21 Vida \n 23 Subasic',bbox=dict(facecolor='none', edgecolor='red', pad=10.0))  
	plt.colorbar(sm)  
	plt.show()  


### Alternative Measures for judging player perfomance ###

# First off get all datasets #
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/8658.json") as url:
    croatia_france = json.loads(url.read().decode())
croatia_france = json_normalize(croatia_france, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/8652.json") as url:
    croatia_russia = json.loads(url.read().decode())
croatia_russia = json_normalize(croatia_russia, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/8656.json") as url:
    croatia_england = json.loads(url.read().decode())
croatia_england = json_normalize(croatia_england, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7581.json") as url:
    croatia_denmark = json.loads(url.read().decode())
croatia_denmark = json_normalize(croatia_denmark, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7545.json") as url:
    data = json.loads(url.read().decode())
croatia_argentina = json_normalize(data, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7529.json") as url:
    croatia_nigeria = json.loads(url.read().decode())
croatia_nigeria = json_normalize(croatia_nigeria, sep = "_")
with urllib.request.urlopen("https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/7561.json") as url:
    croatia_iceland = json.loads(url.read().decode())
croatia_iceland = json_normalize(croatia_iceland, sep = "_")
# Combining all into the same DataFrame:
croatia_all = pd.concat([croatia_argentina, croatia_denmark,croatia_england,
           croatia_france, croatia_nigeria, croatia_russia, croatia_iceland], join = 'outer', sort = False) 
croatia_all = croatia_all[(croatia_all['team_name']=='Croatia')]
total_passes = croatia_all.groupby('team_name')['type_name'].apply(lambda x: (x == 'Pass').sum()).reset_index(name = 'total passes')
total_dribbles = croatia_all.groupby('team_name')['type_name'].apply(lambda x: (x == 'Dribble').sum()).reset_index(name = 'total dribbles')
total_ball_recoveries = croatia_all.groupby('team_name')['type_name'].apply(lambda x: (x == 'Ball Recovery').sum()).reset_index(name = 'total Recoveries')

# Total nr of goals:
croatia_removed_penalties = croatia_all[(croatia_all['period']!= 5)] # Used this to remove goals scored in penalty shootouts
total_goals = croatia_removed_penalties.groupby('player_name')['shot_outcome_name'].apply(lambda x: (x=='Goal').sum()).reset_index(name='Goals')
# Total nr of assists:
total_assists = croatia_all.groupby('player_name')['pass_goal_assist'].apply(lambda x: (x == True).sum()).reset_index(name='Assists')
# Total nr of shots:
total_shots = croatia_all.groupby('player_name')['type_name'].apply(lambda x: (x == 'Shot').sum()).reset_index(name = 'Shots')

# Only Croatia --> Defensive statistics:
def defence(data):
    total_recoveries = data.groupby('player_name')['type_name'].apply(lambda x: (x == 'Ball Recovery').sum()).reset_index(name='Ball_Recoveries')
    total_interceptions = data.groupby('player_name')['type_name'].apply(lambda x: (x == 'Interception').sum()).reset_index(name='Interceptions')
    total_blocks = data.groupby('player_name')['type_name'].apply(lambda x: (x == 'Block').sum()).reset_index(name='Blocks')
    total_clearances = data.groupby('player_name')['type_name'].apply(lambda x: (x == 'Clearance').sum()).reset_index(name='Clearances')
    total_tackles = data.groupby('player_name')['duel_type_name'].apply(lambda x: (x == 'Tackle').sum()).reset_index(name='Tackles')
    total_aerial_duels = data.groupby('player_name')['duel_type_name'].apply(lambda x: (x == 'Aerial Lost').sum()).reset_index(name='Aerial_Duels')
    df_list3 = [total_recoveries, total_interceptions, total_blocks, total_clearances, total_tackles,total_aerial_duels]
    defensive_data = functools.reduce(lambda x,y: pd.merge(x,y, on = 'player_name'), df_list3)
    return defensive_data

summary_defensive_data = defence(croatia_all)
summary_defensive_data = summary_defensive_data.drop('Tackles_y', axis = 1)



def discipline(data):
    total_fouls = data.groupby('player_name')['type_name'].apply(lambda x: (x == 'Foul Committed').sum()).reset_index(name='Fouls_commited')
    yellow_card = data.groupby('player_name')['foul_committed_card_name'].apply(lambda x: (x == 'Yellow Card').sum()).reset_index(name='Yellow_cards')
    red_card = data.groupby('player_name')['foul_committed_card_name'].apply(lambda x: (x == 'Red Card').sum()).reset_index(name='Red_cards')
    yellow_card_behaviour = data.groupby('player_name')['bad_behaviour_card_name'].apply(lambda x: (x == 'Yellow Card').sum()).reset_index(name='Behaviour_yellow')
    red_card_behaviour = data.groupby('player_name')['bad_behaviour_card_name'].apply(lambda x: (x == 'Red Card').sum()).reset_index(name='Behaviour_red')
    df_list4 = [total_fouls, yellow_card, red_card, yellow_card_behaviour, red_card_behaviour]
    discipline_data = functools.reduce(lambda x,y: pd.merge(x,y, on = 'player_name'), df_list4)
    return discipline_data

summary_discipline_data = discipline(croatia_all)
summary_discipline_data = summary_discipline_data.drop('Behaviour_red', axis = 1)
summary_discipline_data['Yellow_Cards'] = summary_discipline_data['Yellow_cards'] + summary_discipline_data['Behaviour_yellow']
summary_discipline_data = summary_discipline_data.drop(['Behaviour_yellow', 'Yellow_cards'], axis = 1)

## Visualizing some stats ##

# Passes:

total_passes = croatia_all.groupby('player_name')['type_name'].apply(lambda x: (x == 'Pass').sum()).reset_index(name='total_passes')
passes = total_passes[total_passes['total_passes'] > 200]

passes = passes.replace({'Luka Modrić': 'Modric', 'Ivan Rakitić': 'Rakitic',
                         'Marcelo Brozović': 'Brozovic', 'Šime Vrsaljko': 'Vrsaljko',
                         'Dejan Lovren': 'Lovren', 'Domagoj Vida': 'Vida', 'Ivan Strinić': 'Strinic', 'Ivan Perišić': 'Perisic'})

sns.barplot(x = 'total_passes', y="player_name", data=passes, palette="OrRd_r")
plt.yticks(fontsize = 60)
plt.xticks(fontsize = 50)
plt.xlabel('Total Passes', fontsize = 30)
plt.title("Most Passes Made", fontsize = 50)
plt.show()

# Dribbles
dribble = total_dribble[total_dribble['total_dribble'] >= 4]

dribble = dribble.replace({'Ante Rebić': 'Rebic', 'Luka Modrić': 'Modric', 'Andrej Kramarić': 'Kramaric',
                           'Ivan Rakitić': 'Rakitic', 'Ivan Strinić': 'Strinic', 'Josip Pivarić': 'Pivaric',
                           'Mateo Kovačić': 'Kovacic', 'Ivan Perišić': 'Perisic', 'Šime Vrsaljko': 'Vrsaljko'})

sns.barplot(x = 'total_dribble', y="player_name", data=dribble, palette="OrRd_r")
plt.yticks(fontsize = 60)
plt.xticks(fontsize = 20)
plt.xlabel('Total Dribbles', fontsize = 30)
plt.title("Top Dribblers", fontsize = 50)
plt.show()

# Passes received #
received = croatia_all.groupby('pass_recipient_name').count()
passes_received = received['pass_recipient_id']
passes_received = pd.DataFrame(passes_received)
passes_received = passes_received.reset_index()
passes_received = passes_received.rename(columns = {'pass_recipient_name': 'player_name'})
passes_received = passes_received.rename(columns = {'pass_recipient_id': 'nr_passes_received'})
receivings = passes_received[passes_received['nr_passes_received']>229]

receivings = receivings.replace({'Luka Modrić': 'Modric', 'Ivan Rakitić': 'Rakitic', 'Ivan Perišić': 'Perisic',
                                 'Šime Vrsaljko': 'Vrsaljko', 'Marcelo Brozović': 'Brozovic', 'Dejan Lovren': 'Lovren',
                                 'Mario Mandžukić': 'Mandzukic', 'Ante Rebić': 'Rebic'})

sns.barplot(x = 'nr_passes_received', y="player_name", data=receivings, palette="OrRd_r")
plt.yticks(fontsize = 60)
plt.xticks(fontsize = 50)
plt.xlabel('Total Passes Received', fontsize = 30)
plt.title("Passes received", fontsize = 50)
plt.show()

## Ball Recoveries
total_recoveries = croatia_all.groupby('player_name')['type_name'].apply(lambda x: (x == 'Ball Recovery').sum()).reset_index(name='Ball_Recoveries')
recoveries = total_recoveries[total_recoveries['Ball_Recoveries']>17]

recoveries = recoveries.replace({'Luka Modrić': 'Modric', 'Danijel Subašić': 'Subasic', 'Ivan Rakitić': 'Rakitic',
                                 'Šime Vrsaljko': 'Vrsaljko', 'Ivan Strinić': 'Strinic', 'Ante Rebić': 'Rebic',
                                 'Dejan Lovren': 'Lovren', 'Marcelo Brozović': 'Brozovic'})

sns.barplot(x = 'Ball_Recoveries', y="player_name", data=recoveries, palette="OrRd_r")
plt.yticks(fontsize = 60)
plt.xticks(fontsize = 20)
plt.xlabel('Total Ball Recoveries', fontsize = 30)
plt.title("Ball Recoveries", fontsize = 50)
plt.show()

## Goals ##
croatia_removed_penalties = croatia_all[(croatia_all['period']!= 5)] # Used this to remove goals scored in penalty shootouts
total_goals = croatia_removed_penalties.groupby('player_name')['shot_outcome_name'].apply(lambda x: (x=='Goal').sum()).reset_index(name='Goals')
goals = total_goals[total_goals['Goals']>0]

goals = goals.replace({'Ivan Perišić': 'Perisic', 'Mario Mandžukić': 'Mandzukic', 'Luka Modrić': 'Modric',
                       'Andrej Kramarić': 'Kramaric', 'Ante Rebić': 'Rebic', 'Domagoj Vida': 'Vida',
                       'Ivan Rakitić': 'Rakitic', 'Milan Badelj': 'Badelj'})

sns.barplot(x = 'Goals', y="player_name", data=goals, palette="OrRd_r")
plt.yticks(fontsize = 60)
plt.xticks(fontsize = 20)
plt.xlabel('Goals', fontsize = 30)
plt.title("Topscorers", fontsize = 50)
plt.show()








