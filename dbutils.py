from pymongo import MongoClient
import datetime
import glob
import os.path
import pymongo
import json
import sys
import itertools

client = MongoClient('mongodb://localhost:27017/')
nbadb = client['nba-database']

games = nbadb.games
team_names = {}

games_key = {}
def insert(game):
    vt = game["vt"]
    ht = game["ht"]
    date = game["date"]
    #remove the old one and insert the new one
    print nbadb.games.remove({"vt": vt, "ht": ht, "date": date})
    game_id = games.insert(game)
    return game_id

def drop():
    nbadb.games.drop()

def init():
#     game_0 = {
#         "vt": "GSW",
#         "ht" : "CAV",
#         "vs" : "188",
#         "hs" : "29",
#         "time" : "FINAL", #TODO: format time, final?
#         "date" : datetime.datetime(2017, 1, 30),
#         "created_date" : datetime.datetime.utcnow()
#         }
#     game_1 = {
#         "vt": "GSW",
#         "ht" : "CAV",
#         "vs" : "123",
#         "hs" : "30",
#         "time" : "FINAL", #TODO: format time, final?
#         "date" : datetime.datetime(2017, 2, 1),
#         "created_date" : datetime.datetime.utcnow()
#         }
#     game_2 = {
#         "vt": "GSW",
#         "ht" : "CAV",
#         "vs" : "-1",
#         "hs" : "-1",
#         "time" : "17:00 ET", #TODO: format time, final?
#         "date" : datetime.datetime(2017, 2, 6),
#         "created_date" : datetime.datetime.utcnow()
#         }

#     game_3 = {
#         "vt": "GSW",
#         "ht" : "CAV",
#         "vs" : "-1",
#         "hs" : "-1",
#         "time" : "17:00 ET", #TODO: format time, final?
#         "date" : datetime.datetime(2017, 2, 7),
#         "created_date" : datetime.datetime.utcnow()
#         }
#     id = insert(game_1)
#     insert(game_0)
#     insert(game_2)
#     insert(game_3)
#     print id
    print "test"
# return last game and next game of this team, given the current date

def dump():
    for game in nbadb.games.find():
        print game
#date is the server time(pacific time)
def convertDatetoET(date):
    date = date + datetime.timedelta(hours=3)
    date = datetime.datetime(date.year, date.month, date.day)
    return date
# GSW's tomorrwo's game
# TODO: test
def searchByTeamAndDate(team_name, date):
    date = convertDatetoET(date)
    res_games = list(nbadb.games.find({"$and" : [{"date" : date}, { "$or" : [{"ht" : team_name}, {"vt" : team_name}] }]}))

# GSW's game
# GSW's prev game
# GSW's next game
def searchByOneTeam(team_name, current_date = datetime.datetime.utcnow() - datetime.timedelta(hours=4)):
    current_date = datetime.datetime(current_date.year, current_date.month, current_date.day)
    last_game = None
    next_game = None
    print len(list(nbadb.games.find({"vt": team_name}))) #bug should, right now today's game is always next game, fix!!
    res_games = list(nbadb.games.find({"$and" : [{"$or" : [ {"vt": team_name}, {"ht": team_name} ]}, {"date": {"$lte" : current_date}}]}) \
                    .sort("date"))
    if (len(res_games) == 0):
        print "No Game info found"
    else:
        game = res_games[-1] # after sort, the larger date will be at the end
        if (game['time'] != 'FINAL'): #haven't start yet
            next_game = game
        else:
            last_game = game

    if (next_game == None): #today's game has finished, so try to find future game
        res_games = list(nbadb.games.find({"$and" : [{"$or" : [ {"vt": team_name}, {"ht": team_name} ]}, {"date": {"$gt" : current_date}}]}) \
                    .sort("date"))
        if (len(res_games) == 0):
            print "No future game found"
        else:
            for g in res_games: #filter by final keyword
                if (g['time'] != 'FINAL'):
                    next_game = g
                    break
                print "No future game found"
    else: #today's game hasn't finished yet, so try to find the prev game
        print current_date
        res_games = list(nbadb.games.find({"$and" : [{"$or" : [ {"vt": team_name}, {"ht": team_name} ]}, {"date": {"$lt" : current_date}}]}) \
                    .sort("date"))
        if (len(res_games) == 0):
            print "No prev game found"
        else:
            last_game = res_games[-1]
    print "last game:"
    print last_game
    print "next_game:"
    print next_game
    return last_game, next_game

def searchByTwoTeams(team_name_1, team_name_2, current_date):
    current_date = datetime.datetime(current_date.year, current_date.month, current_date.day)
    last_game = None
    next_game = None
    return "text"

def searchByDate(date):
    res_games = list(nbadb.games.find({"date": date}))
    return res_games

def load(filename):
    with open(filename) as f:
        for line in f:
            # slice the next 6 lines from the iterable, as a list.
            lines = [line] + list(itertools.islice(f, 8))
            game = json.loads(''.join(lines))
            game_key = game['vt'] + game['ht'] + game['date']
            ymd = game['date'].split('-')
            year = int(ymd[0])
            month = int(ymd[1])
            day = int(ymd[2])
            game['date'] = datetime.datetime(year, month, day)
            if game_key in games_key: #bug, why dup here??
                #print file
                print game_key
            else:
                insert(game)
                games_key[game_key] = 1
            #print insert(game)

def loadAll():
    path = "/Users/yuanzhedong/Documents/mobvoi/nba-crawler/nbademo/data/"
    for fname in glob.glob(os.path.join(path,"*.txt.json")):
        load(fname)

def test():
    print searchByOneTeam("GSW")

def update(vt, vs, ht, hs, year, month, day):
    game_0 = {
        "vt": vt,
        "ht" : ht,
        "vs" : vs,
        "hs" : hs,
        "time" : "FINAL", #TODO: format time, final?
        "date" : datetime.datetime(year, month, day),
        "created_date" : datetime.datetime.utcnow()
        }
    print nbadb.games.remove({"vt": vt, "ht": ht, "date": datetime.datetime(year, month, day)})
    print nbadb.games.insert(game_0)

def delete():
    print nbadb.games.delete_many({"ht" : "GSW"})
    nbadb.games.delete_many({"vt" : "GSW"})
    nbadb.games.delete_many({"ht" : "CAV"})
    nbadb.games.delete_many({"vt" : "CAV"})

def checkDate(year, month, day):
    res_games = list(nbadb.games.find({"date" : datetime.datetime(year, month, day)}))
    for g in res_games:
        print g['vt'], g['vs'], g['ht'], g['hs'], g['date']
if __name__ == "__main__":
    #drop()
    #loadAll()
    checkDate(2017, 1, 31)
    load(sys.argv[1])
    #drop()
    # delete()
    # update("Denver Nuggets", 108, "Minnesota Timberwolves", 111, 2017, 1, 22)
    # update("Phoenix Suns", 115, "Toronto Raptors", 103, 2017, 1, 22)
    # update("Los Angeles Lakers", 73, "Dallas Mavericks", 122, 2017, 1, 22)
    checkDate(2017, 1, 31)
    # test()
    #update("Washington Wizards", 109, "Charlotte Hornets", 99, 2017, 1, 23)
    #update("San Antonio Spurs", 112, "Brooklyn Nets", 86, 2017, 1, 23)
    #update("LA Clippers", 115, "Atlanta Hawks", 105, 2017, 1, 23)
    #update("Golden State Warriors", 102, "Miami Heat", 105, 2017, 1, 23)
    #update("Sacramento Kings", 109, "Detroit Pistons", 104, 2017, 1, 23)
    #update("Houston Rockets", 114, "Milwaukee Bucks", 127, 2017, 1, 23)
    #update("Cleveland Cavaliers", 122, "New Orleans Pelicans", 124, 2017, 1, 23)
    #update("New York Knicks", 109, "Indiana Pacers", 103, 2017, 1, 23)
    #update("Oklahoma City Thunder", 97, "Utah Jazz", 95, 2017, 1, 23)
