# -*- coding: utf-8 -*-
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

import sys
import datetime
import dbutils
from wit import Wit
from bson import json_util
import json

import logging

app = Flask(__name__)

# TODO: thread safe
bot_response = ""

eng2Chi = {
    'Atlanta Hawks': u'老鹰',
    'Boston Celtics':  u'凯尔特人',
    'Brooklyn Nets': u'篮网',
    'Charlotte Hornets': u'黄蜂',
    'Chicago Bulls': u'公牛',
    'Cleveland Cavaliers': u'骑士',
    'Dallas Mavericks' : u'小牛',
    'Denver Nuggets' : u'掘金',
    'Detroit Pistons': u'活塞',
    'Golden State Warriors': u'勇士', 
    'Houston Rockets': u'火箭',
    'Indiana Pacers': u'步行者',
    'LA Clippers': u'快船',
    'Los Angeles Lakers': u'湖人',
    'Memphis Grizzlies': u'灰熊',
    'Miami Heat': u'热火',
    'Milwaukee Bucks': u'雄鹿',
    'Minnesota Timberwolves': u'森林狼',
    'New Orleans Pelicans': u'鹈鹕',
    'New York Knicks': u'尼克斯',
    'Oklahoma City Thunder': u'雷霆',
    'Orlando Magic': u'魔术',
    'Philadelphia 76ers': u'76人',
    'Phoenix Suns': u'太阳',
    'Portland Trail Blazers': u'开拓者',
    'Sacramento Kings'  : u'国王',
    'San Antonio Spurs' : u'马刺',
    'Toronto Raptors' : u'猛龙',
    'Utah Jazz' : u'爵士',
    'Washington Wizards': u'奇才',
    }

def CvEngtoChi(eteam):
    global eng2Chi
    return eng2Chi[eteam]

def CvChitoEng(chn):
    global eng2Chi
    for key in eng2Chi.keys():
        if eng2Chi[key] == chn:
            return key
    print type(chn), chn
    print "team not found!!!"
    return None

def normTime(time):
    time_chi = ''

    if ' PM' not in time:
        time_chi = "上午"
    else:
        time_chi = "下午"

    time = time.split(' ')[0]
    time_chi = time_chi.decode('utf8') + time
    return time_chi

def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def send(request, response):
    print(response['text'])
    global bot_response
    bot_response = response['text']
    #TODO: remove trail {}
    bot_response = bot_response.split('{')[0]
    print bot_response

def get_forecast(request):
    context = request['context']
    entities = request['entities']

    loc = first_entity_value(entities, 'location')
    if loc:
        context['forecast'] = 'sunny'
        if context.get('missingLocation') is not None:
            del context['missingLocation']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']

    return context

def normDate(date):
    date = date.split(" ")[0]
    date = date.split("-")
    m = date[1]
    d = date[2]
    return m + "月" + d + "日"

def do_action(request):
    context = request['context']
    entities = request['entities']
    print context
    #print entities['intent'][0]['value']
    intent = first_entity_value(entities, 'intent')
    if intent == None:
        return no_intent(request)
    #TODO: prev_game, next_game
    user_intent = entities['intent'][0]['value']
    if (user_intent == 'next_game'):
        logging.info("Try get next game")
        context['welcome'] = False
        return get_next_game(request)
    else: #intent = prev_game
        if (user_intent == "entrance"):
            context['welcome'] = True
            return context
        logging.info("Try get prev game")
        context['welcome'] = False
        return get_prev_game(request)

def no_intent(request):
    context = request['context']
    context['welcome'] = True #
    return context

def get_prev_game(request):
    context = request['context']
    entities = request['entities']

    team = first_entity_value(entities, 'team')
    #TODO: add time
    #current_date = datetime.datetime(2017, 2, 1)
    print team
    team = CvChitoEng(team)
    print team
    #TODO: add team word list
    if team:
        last_game, next_game = dbutils.searchByOneTeam(team)
        context['team'] = team
        context['prevGame'] = True
        comp = None
        comp_score = None
        team_score = None
        date = None
        time = None
        isHome = True
        if last_game:
            comp = last_game['vt']
            comp_score = last_game['vs']
            team_score = last_game['hs']
            if (comp == team):
                comp = last_game['ht']
                comp_score = last_game['hs']
                team_score = last_game['vs']
                isHome = False
            date = str(last_game['date'])
            context['comp'] = comp
            context['comp_chi'] = CvEngtoChi(comp)
            context['team_chi'] = CvEngtoChi(team)
            context['date'] = normDate(date)
            #context['time'] = normTime(time)
            context['comp_score'] = comp_score
            context['team_score'] = team_score
        else:
            context['noNextGame'] = True
            print "no next game"
        #TODO: check none
        #context['lastGame'] = json.dumps(last_game, default=json_util.default)
        #context['nextGame'] = json.dumps(next_game, default=json_util.default)
    else:
        context['missingTeam'] = True
        if context.get('lastGame') is not None:
            del context['lastGame']
        if context.get('nextGame') is not None:
            del context['nextGame']
    return context

def get_next_game(request):
    context = request['context']
    entities = request['entities']

    team = first_entity_value(entities, 'team')
    #TODO: add time
    #current_date = datetime.datetime(2017, 2, 1)
    #print team
    team = CvChitoEng(team)
    print team
    #TODO: add team word list
    if team:
        # TODO: set prevGame to be False??
        context['nextGame'] = True
        last_game, next_game = dbutils.searchByOneTeam(team)
        context['team'] = team
        comp = None
        date = None
        time = None
        if next_game:
            comp = next_game['vt']
            if (comp == team):
                comp = next_game['ht']
            date = str(next_game['date'])
            time = next_game['time']
            context['comp'] = comp
            context['comp_chi'] = CvEngtoChi(comp)
            context['team_chi'] = CvEngtoChi(team)
            context['date'] = normDate(date)
            context['time'] = normTime(time)
        else:
            context['noNextGame'] = True
            print "no next game"
        #TODO: check none
        #context['lastGame'] = json.dumps(last_game, default=json_util.default)
        #context['nextGame'] = json.dumps(next_game, default=json_util.default)
    else:
        context['missingTeam'] = True
        if context.get('lastGame') is not None:
            del context['lastGame']
        if context.get('nextGame') is not None:
            del context['nextGame']
    return context

actions = {
        'send': send,
        'getForecast': get_forecast,
        'getNextGame': get_next_game,
        'getPrevGame': get_prev_game,
        'doAction': do_action,
        }
#access_token = "MMTMEGIUJXBVS3PP3W6DOMVQ7LFWIKGR"
access_token = "TBIJBYZSHJNFS4EEVVCYEDJ2KPM3ZIAT"
client = Wit(access_token=access_token, actions=actions)

context = {}

@app.route('/bot', methods=['GET'])
def run_query():
    # resp = client.message('GSW game')
#     context = {}
#     session_id = 'my-user-session-43'
    #resp = client.converse('my-user-session-42', 'GSW game', {})
    #print('Yay, got Wit.ai response: ' + str(resp))
    #print actions
#    context = client.run_actions(session_id, 'GSW game')
    #
    #return jsonify({'result' : str(resp)})
    message = request.args.get('query')
    session_id = request.args.get('sid')
    print session_id
    print message.encode('utf-8')
    context = client.run_actions(session_id, message, verbose=False)
    print bot_response
    print "###"
    return jsonify({'result' : context, 'message' : bot_response})

if __name__ == '__main__':
    logging.basicConfig(filename='app.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    app.run(host='0.0.0.0', port=9005, debug=True)
