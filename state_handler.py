#/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
state_handler.py
---------------------------------------------------------------


This file is contains functions that handle the bot states and relays
the information to the database as well as the api.

Created by Nick Tantivasadakarn.
"""

import random
import time
from collections import defaultdict
from os import system
from pymongo import MongoClient
from shallow_bot_parser import all_shallow_bots


TIMEOUT_SECONDS = 3600

class StateHandler():
    """
    Class variables:
        self.db (mongo client) -- database object
        self.self.id2bot(dict) -- user_id to current bot dictionary
        self.id2state(dict) -- user_id to bot state dictionary 
                                (will be reset after each conversation)
        self.id2parameters(dict) -- user_id to parameters 
                                (will persist after a conversation)
        self.id2name(dict) -- user_id to name dictionary

    """

    def __init__(self, bot_folder, db_name= 'TelegramPopBots'): #, reply_dict, **kwargs):

        #initialize bot responses and parameters
        self.reply_dict = []

        #initialize database
        self.db = MongoClient()[db_name]
        self.db.startup_log.insert_one({'start_up_time': time.time()})
        self.central_bot_list = all_shallow_bots('./Intro_bots')
        self.bot_list = all_shallow_bots(bot_folder)

        #initialize user info 
        self.id2bot = defaultdict(lambda:None) #dictionary that links the user id to the bot id
        self.id2state = defaultdict(lambda:None) #dictionary that links the user id to states
        self.id2name, self.id2parameters, self.subj_ids = self.load_parameters(self.db.user_history)

    def get_response(self, user_id, query):
        """
        Gets the response from the bot given the query. It will make a call to the 
        'get_response' function within the bots.

        If the bot has ended, it will jump the user back to the central bot.
        """

        bot = self.id2bot[user_id]
        if not bot:
            bot = self.id2bot[user_id] = self.recommend_bot()
        prev_state = self.id2state[user_id]
        new_state, response, buttons = bot.get_response(user_id, query, prev_state)
        
        if new_state:
            self.id2state[user_id] = new_state
            #handle_bot_commands(user_id, query):
            self.log_response(user_id, query, bot.name, bot.id, new_state, response)
            return response, buttons
        else: #If bot is finished return to the central bot.
            self.id2bot[user_id] = self.central_bot_list[0]
            self.id2state[user_id] = new_state
            return self.get_response(user_id, query)

    def log_response(self, user_id, query, bot_name, bot_id, bot_state, response):
        """
        Logs the response to the database

        Parameter:
            response(list) -- list of responses
        """
        
        new_entry = {
                'bot_id': bot_id,
                'bot_name': bot_name,
                'bot_state':bot_state,
                'query': query,
                'response': response,
                'time': time.time()
            }
        self.db.user_history.update_one({'user_id':user_id},
                                {"$push":{'user_history': new_entry}}
                            )

    def handle_bot_commands(self, user_id, query):
        """
        Handles commands of the bot in a certain state
        """
        pass

    def load_parameters(self, collection):
        """
        Loads names and user parameter from database

        Parameter:
            collection (mongo collection)

        Returns:
            (dict) user_id to user_name dictionary
        """
        names = defaultdict(lambda: '')
        parameters = defaultdict(dict)
        subj_ids = defaultdict(lambda: None)
        for hist in collection.find():
            names[hist['user_id']] = hist.get('user_name', '')
            parameters[hist['user_id']] = hist.get('user_parameters', {})
            subj_ids[hist['user_id']] = hist.get('subject_id', None)
        return names, parameters, subj_ids



    def recommend_bot(self):
        """
        Currently set to random.

        Return:
            bot (bot object)
        """
        return random.choice(self.bot_list)




if __name__ == '__main__':
    sh = StateHandler('./example_bots')
    print('###')
    # sh.id2bot[1111] = sh.recommend_bot()
    # sh.id2state[1111] = 'bot_opening'
    print(sh.get_response(1111, 'test'))
    print(sh.get_response(1111, 'yes'))
