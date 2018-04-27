import tkinter
import requests
import json
import networkx as nx
import matplotlib.pyplot as plt
import time

rootSteamID = 76561198011615406
apiKey = '96F8B7409A4E22A292CA359CF32C58D7'
getDataFlag = False
limiter = 50

def draw_graph(graph):

    # extract nodes from graph
    nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])

    # create networkx graph
    G=nx.Graph()

    # add nodes
    for node in nodes:
        G.add_node(node)

    # add edges
    for edge in graph:
        G.add_edge(edge[0], edge[1],weight=.1, color='black')

    edges = G.edges()
    colors = [G[u][v]['color'] for u,v in edges]
    weights = [G[u][v]['weight'] for u,v in edges]


    # draw graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels = True, edges=edges, edge_color=colors, width=weights, node_size=500, node_color='grey')

    # show graph
    nx.write_gexf(G, 'graph.gexf')
    plt.show()

def grabAllFriends(steamID):
    friend = {'key': apiKey, 'steamid': steamID, 'relationship': 'friend'}
    friendListUrl = "http://api.steampowered.com/ISteamUser/GetFriendList/v0001/"
    r = requests.get(friendListUrl, params=friend)
    friendsList = r.json()['friendslist']['friends']
    steamIDList = []
    
    for friend in friendsList:
        steamIDList.append(friend['steamid'])
    return steamIDList

def grabAllFriendProfiles(friendIDList):
    friendString = ''
    for steamid in friendIDList:
        friendString= friendString+steamid+','

    standard = {'key': '96F8B7409A4E22A292CA359CF32C58D7', 'steamids': friendString}
    userProfile = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    r = requests.get(userProfile, params=standard)

    summaryList = r.json()['response']['players']
    friendList = []
    for friend in summaryList:
        friendList.append(friend)
    return friendList

def generateTouples(rootName,friendNameList):
    toupleList = []
    for friend in friendNameList:
        t  = (rootName, friend['personaname'])
        toupleList.append(t)
    return toupleList

def dumpToFile(filename,contents):
    with open('data/'+filename, 'w') as outfile:
        json.dump(contents, outfile)

def grabUserProfile(steamID):
    standard = {'key': apiKey, 'steamids': steamID}
    userProfile = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    r = requests.get(userProfile, params=standard)
    profile = r.json()['response']['players'][0]
    return profile

def gatherData():
    idCounter = 0
    #Root User
    print('Processed - Root - MrGWilliam')
    root = grabUserProfile(rootSteamID)
    rootFriendIDs = grabAllFriends(rootSteamID)
    rootFriends = grabAllFriendProfiles(rootFriendIDs)

    dumpToFile('user_'+str(idCounter)+'.json',root)
    dumpToFile('friends_'+str(idCounter)+'.json',rootFriends)

    
    for friendID in rootFriendIDs:
        idCounter = idCounter+1
        try:
            user = grabUserProfile(friendID)
            userFriendIDS = grabAllFriends(friendID)
            userFriends = grabAllFriendProfiles(userFriendIDS)

            dumpToFile('user_'+str(idCounter)+'.json',user)
            dumpToFile('friends_'+str(idCounter)+'.json',userFriends)
            print('Processed - Friend - '+user['personaname'])
        except:
            dumpToFile('user_'+str(idCounter)+'.json',[])
            dumpToFile('friends_'+str(idCounter)+'.json',[])
            print('Processed - Friend - '+user['personaname'])

def createGraph():
    graph = []
    idCounter = 0
    # Load Root
    with open('data/user_'+str(idCounter)+'.json') as fd:
        user = json.load(fd)
        print('generating for ' +user['personaname']+' - '+str(idCounter))
    with open('data/friends_'+str(idCounter)+'.json') as fd:
        friends = json.load(fd)
    graph = generateTouples(user['personaname'], friends)

    idCounter = 1

    for x in range(0, limiter):
        try:
            # Load Root
            with open('data/user_'+str(idCounter)+'.json') as fd:
                user = json.load(fd)
                print('generating for ' +user['personaname']+' - '+str(idCounter))
            with open('data/friends_'+str(idCounter)+'.json') as fd:
                friends = json.load(fd)
            graph = graph + generateTouples(user['personaname'], friends)
            
        except:
            pass
        idCounter = idCounter+1
    return graph
    
# Gather Data
if getDataFlag:
    gatherData()

graph = createGraph()
draw_graph(graph);
