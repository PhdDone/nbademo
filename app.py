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

app = Flask(__name__)

# TODO: thread safe
bot_response = ""

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

def get_next_game(request):
    context = request['context']
    entities = request['entities']

    team = first_entity_value(entities, 'team')
    #TODO: add time
    #current_date = datetime.datetime(2017, 2, 1)
    print team
    #TODO: add team word list
    if team:
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
            context['date'] = normDate(date)
            context['time'] = time
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
        }
access_token = "MMTMEGIUJXBVS3PP3W6DOMVQ7LFWIKGR"

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
    app.run(host='0.0.0.0', port=9005, debug=True)
