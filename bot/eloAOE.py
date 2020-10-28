import io
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import requests
import json
import random
from discord import Embed, File
from datetime import datetime

SOLO_GAME_MODE = '3'
TEAM_GAME_MODE = '4'

def get_player_leaderboard_response(playerName, gameMode):
    apiUrl = 'https://aoe2.net/api/leaderboard?game=aoe2de&leaderboard_id=' + gameMode + '&start=1&count=10&search=' + playerName
    try:
        response = requests.get(apiUrl)
    except Exception as err:
        errorResponse = {'error': 'Error with request to ' + apiUrl}
        json_print(errorResponse)
        return 1
    jsonResponse = response.json()
    if not jsonResponse.get('leaderboard'):
        raise PlayerNotFound('Couldn\'t find any player called ' + playerName)
    return jsonResponse

def get_player_data(playerName, gameMode):
    playerLeaderboard = get_player_leaderboard_response(playerName, gameMode)
    return get_player_data_from_json(playerLeaderboard, playerName, gameMode)

def get_player_history(playerName, matches, gameMode = SOLO_GAME_MODE):
    playerData = get_player_data(playerName, gameMode)
    apiUrl = 'https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=' + gameMode + '&count=' + str(matches) + '&steam_id=' + playerData['steamId']
    try:
        response = requests.get(apiUrl)
    except Exception as err:
        errorResponse = {'error': 'Error with request to ' + apiUrl}
        json_print(errorResponse)
        return 1
    return get_player_history_for_print(response.json(), playerData['name'], playerData['currentRankData'])

def json_print(jsonStr):
    print(json.dumps(jsonStr, sort_keys=False, indent=4))

def get_printable_elo_values(playersData, gameMode, playerName):
    index = 0
    if len(playersData) > 1:
        index = get_exact_player(playersData, playerName)
    leaderboardData = playersData[index]
    response = {}
    responseData = []
    response['title'] = ''
    if (gameMode == SOLO_GAME_MODE):
        title = leaderboardData['name'] + ' Solo Niceness'
    elif (gameMode == TEAM_GAME_MODE):
        title = leaderboardData['name'] + ' Shared Niceness'
    responseData.append(get_response_item(leaderboardData, 'rating'))
    responseData.append(get_response_item(leaderboardData, 'rank'))
    responseData.append(get_response_item(leaderboardData, 'highest_rating'))
    responseData.append(get_response_item(leaderboardData, 'games'))
    response['playerStats'] = '\n'.join(responseData)
    response['title'] = title
    return response

def get_response_item(leaderboardData, item):
    return item + ': **' + str(leaderboardData[item]) + '**'

def get_player_data_from_json(playerLeaderboardJson, playerName, gameMode):
    index = 0
    playersData = playerLeaderboardJson.get('leaderboard')
    currentRankData = get_printable_elo_values(playersData, gameMode, playerName)
    if len(playersData) > 1:
        index = get_exact_player(playersData, playerName)
    return {'steamId': playersData[index]['steam_id'], 'name': playersData[index]['name'], 'currentRankData': currentRankData}

def get_exact_player(playersData, playerName):
    for i in range(0, len(playersData)):
        if (playersData[i]['name'] == playerName):
            return i
    return 0

def get_player_history_for_print(playerHistoryJson, playerName, currentRankData):
    matchDates = []
    matchRatings = []
    matchDateLabels = []

    for v in playerHistoryJson:
        date = datetime.fromtimestamp(v['timestamp'])
        matchDates.append(str(date.year) + '#' + str(date.day) + ' / ' + str(date.month) + '#' + str(date.hour) + ':' + str(date.minute))
        matchDateLabels.append(str(date.day) + ' - ' + str(date.strftime("%b")))
        matchRatings.append(v['rating'])

    taunt = get_taunt(matchRatings, playerName)
    matchDates.reverse()
    matchRatings.reverse()
    matchDateLabels.reverse()
    trimmedxLabels = get_trimmed_xLabels(matchDateLabels)
    xLabels = remove_repeated_dates(trimmedxLabels)
    axes = {'dates':matchDates, 'ratings':matchRatings, 'dateLabels': xLabels, 'playerName': playerName, 'taunt': taunt, 'currentRankData': currentRankData}
    return axes

def remove_repeated_dates(matchDates):
    lastDate = ''
    xLabels = []
    for date in matchDates:
        if (date == lastDate or date == ''):
            xLabels.append('')
        else:
            lastDate = date
            xLabels.append(date)
    return xLabels

def get_trimmed_xLabels(xLabels):
    # When there are too many xLabels, consecutive ones will be skipped to avoid overlapping
    # Ensures there's a distance of n steps between labels

    maxReadableLabels = 20
    labelsCount = len(xLabels)
    if (labelsCount <= maxReadableLabels):
        return xLabels
    newLabels = []
    stepSize = int(labelsCount / maxReadableLabels)
    for i in range(0,len(xLabels)):
        if not (i % stepSize == 0):
            newLabels.append('')
        else:
            newLabels.append(xLabels[i])
    return newLabels

def get_taunt(ratings, playerName):
    taunt = ''
    if len(ratings) < 10:
        return taunt;
    average = sum(ratings) / len(ratings)
    current = ratings[0]
    compare = ratings
    minElo = min(compare)
    maxElo = max(compare)

    if (current < average):
        taunt = get_taunt_bad(playerName)

    if (current > maxElo - (maxElo - average) / 2):
        taunt = get_taunt_good(playerName)
    return taunt


def get_taunt_bad(playerName):
    taunts = [
        'All hail, king of the losers!',
        'Sure, blame it on your ISP.',
        'My granny could scrap better than that.',
        'Told ya to pick goths...',
        'Last excuse: "*Yeah, well, you should see the other guy.*"',
        'Last excuse: "*Odsblood! I accidentally resigned by mistake.*"',
        'Last excuse: "*My townsfolk began too close to mine kingdom\'s Town Center.*"',
        'Last excuse: "*Far too many birds flew over mine kingdom.*"',
        'Last excuse: "*A mere a single scout was present to serve in the beginning.*"',
        'Last excuse: "*My sheep perished when my folk sought to use it as food.*"',
        'Last excuse: "*Forsooth, I couldst not tame any wolves.*"',
        'Last excuse: "*All my beginning citizenry were male.*"',
        'Last excuse: "*Thy heraldic color was superior to mine own.*"',
        'Last excuse: "*My ignorant folk couldst not replant the berries!*"',
        'Last excuse: "*Thou art human, with soul and wit. I am naught but clockwork!*"',
        'Last excuse: "*My throne was most uncomfortable.*"',
        'Last excuse: "*Forsooth, the nearby boars grunted too loudly and frequently.*"',
        'Last excuse: "*Zounds! I couldst not build a Wonder in the Dark Age!*"',
        'Last excuse: "*I couldst not comprehend mine folks\' speech!*"',
        'Last excuse: "*My peasants wert puling wretches (a puny 25 hit points)!*"',
        'Last excuse: "*The shore fish near mine villager appeared all too sleepy.*"',
        'Last excuse: "*A graceless hillock rose too near my Town Center.*"',
        'Last excuse: "*My peasants\' huts all faced different directions!*"',
        'Last excuse: "*The deer fled when mine hunters sought to slay them.*"',
        'Last excuse: "*When I commanded a peasant to hunt fierce boar, it slew him.*"',
        'Last excuse: "*My peasants foolishly walk on foot instead of astride ponies.*"',
        'Last excuse: "*Alas, I could find naught but fools gold.*"',
        'Last excuse: "*No wonder thou wert victorious! I shalt abdicate*".',
        'Last excuse: "*DAAAHH! ME RE CAGARON!*".',
        'Have you tried 40 min boom into Konniks?',
        'Have you tried Apex Legends instead?',
        'All you have to do is just follow Okita\'s advice'
    ]

    return playerName + ' elo isn\'t nice looking...\n' +  random.choice(taunts)

def get_taunt_good(playerName):
    taunts = [
        'All hail, king of the nices!',
        'But who could lose with goths anyway?',
        'Proud graduate of the DatApo Center For Kids Who Can\'t Farm Good And Wanna Learn To Do Other Stuff Good Too',
        'Its time to open that Twitch stream',
        'Looks like a good moment to start loving money...',
        'RAIDING PARTY!',
        'Next objective: beat DatApo and Okita in a 1vs2',
        'But next time try to win Arena without portuguese'
    ]
    return 'That ' + playerName + '\'s so hot right now...\n' + random.choice(taunts)

def generate_elo_plot(axesData) -> io.BytesIO:
    dates = axesData['dates']
    ratings = axesData['ratings']
    dateLabels = axesData['dateLabels']
    fullPlayerName = axesData['playerName']
    
    backgroundGreyColor = '#2c2f33'
    discordGreyColor = 0x2c2f33
    discordBlueColor = '#7289da'
    discordLightGrey = '#99aab5'

    plt.figure(figsize=(30, 15), facecolor=backgroundGreyColor)
    plt.plot(dates, ratings, 'wo-', color=discordBlueColor, markerfacecolor=discordLightGrey, linewidth=4, markersize=12)
    plt.margins(0.01)
    axes = plt.gca()
    axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    axes.set_axisbelow(True)
    axes.yaxis.grid(color='gray', linestyle='dashed')
    axes.xaxis.grid(color='gray', linestyle='dashed')

    figure = plt.gcf()
    plt.style.use('dark_background')
    plt.suptitle(fullPlayerName + ' Niceness', color="#FFFFFF", fontsize=50)
    plt.xticks(dates, dateLabels)
    yUpperTick = round(max(ratings) + 40, -1)
    yLowerTick = round(min(ratings) - 30, -1)
    yTicksCount = 14

    plt.yticks(range(yLowerTick, yUpperTick, int((yUpperTick - yLowerTick) / yTicksCount)) )
    axes.tick_params(axis='x', rotation=60, colors="#FFFFFF", labelsize=26, pad=10)
    axes.tick_params(axis='y', colors="#FFFFFF", labelsize=26, pad=16)
    axes.set_facecolor(backgroundGreyColor)
    figure.set_facecolor('w')
    buf = io.BytesIO()
    plt.savefig(buf, transparent=False, format='png', facecolor=backgroundGreyColor)
    buf.seek(0)
    plot = File(
        fp=buf,
        filename='eloGraph.png'
    )
    embed = Embed(
        title=axesData['currentRankData']['title'],
        colour=discordGreyColor,
        description=axesData['currentRankData']['playerStats']
    )
    embed.set_image(url=f'attachment://eloGraph.png')
    return [plot, embed]

class PlayerNotFound(Exception):
    pass