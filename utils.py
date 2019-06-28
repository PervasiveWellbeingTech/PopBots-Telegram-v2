#/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Contains methods for processing text, getting features,
and defining fixed parameters.

Created by Nick Tantivasadakarn
Modified from scripts by Honghao Wei.
"""

import random
import string
import nltk
from rake_nltk import Rake
from enum import Enum

     
from collections import *
r = Rake()

class Params:
    def __init__(self, bot_num=9, sleeping_time=2, abtest_choice=-1, bot_choice=-1):
        """
        Initializes the bot that will be used in the system.

        Notes: 
        - All new bot information must be added here.
        - bot_name_list refers to the actual name of the bot.
        - bot_tech_name_list refers to the method that the bot employs.
            (bots are manually evoked using this name.)

        """

        self.BOT_NUM = bot_num
        self.SLEEPING_TIME = sleeping_time
        self.ABTEST_CHOICE = abtest_choice #   -1 random choice, > -1, the index of selected reply
        self.BOT_CHOICE = bot_choice # -1 random, 0 worse case bot, 1 problem solving bot, 2 positive thining bot
        self.MODE = Modes.TEXT
        assert self.BOT_CHOICE < self.BOT_NUM, 'Bot_num: {}, Bot_choice: {}'.format(self.BOT_NUM, self.BOT_CHOICE)
        
        ##########Bot list##########
        self.bot_name_list = ['Doom Bot', 'Sherlock Bot', 'Glass-half-full Bot', 'Sir Laughs Bot', 'Chill bot', 'Treat yourself Bot', 'Dunno Bot', 'Onboarding Bot', 'Checkin Bot']
        self.bot_tech_name_list = ['worst case', 'problem solving', 'positive thinking', 'humor', 'relaxation', 'self love', 'distraction', 'introduce', 'check']
 
    def set_sleeping_time(self, sleeping_time):
        self.SLEEPING_TIME = sleeping_time

    def set_bot_choice(self, bot_choice):
        self.BOT_CHOICE = bot_choice
        assert self.BOT_CHOICE < self.BOT_NUM, 'Bot_num: {}, Bot_choice: {}'.format(self.BOT_NUM, self.BOT_CHOICE)

    def set_mode(self, mode):
        if mode == 'text':
            self.MODE = Modes.TEXT
        elif mode == 'voice':
            self.MODE = Modes.VOICE


class Config:
    """
    Contains standard 
    """
    def __init__(self):
        self.OPENNING_INDEX = -1
        self.CLOSING_INDEX = -2
        self.START_INDEX = -3
        self.DK_INDEX = -4
        self.ARE_YOU_DONE_INDEX = -5
        self.CONTINUE_INDEX = -6
        self.ABRUPT_CLOSING_INDEX = -7
        self.QUESTION_INDEX = -8


        self.DEFAULT_YES = ['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay']
        self.DEFAULT_NO = ['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na']
        self.DEFAULT_DK = ["dk", "dunno", "dno", "don't know", "idk"]
        self.GREETINGS = ['hi','hey', 'hello']
        self.DEFAULT_OTHERS = "__OTHERS__"

class Modes(Enum):
    GENERAL = 'general'
    TEXT = 'text'
    VOICE = 'voice'



class Reply:
    """
    A class representing a bot 

    Parameters:
        bot_id (int) -- id of the bot
        response_id (int) -- id of a response within a bot
        texts (list) -- list of strings winthin a reply 
                        Format: [['Hi', 'How are you?'], ['Howdy']]
        next_id (int or list) -- integer of the next reply or a list of tuples
                                in the form (pattern, int) to do choices.
        image (path) -- path to image. (optional)
                        Note: images are displayed before text.
        commands(set) -- set of special commands (optional)
    """
    def __init__(self, bot_id, response_id, texts, next_id, image=None, commands={}):
        self.bot_id = bot_id
        self.response_id = response_id
        self.texts = texts
        self.next_id = next_id
        self.image = image
        self.commands = commands


def find_keyword(input_str, word_list):
    """
    Loops through each word in the input string.
    Returns true is there is a match.

    Parameters:
        input_str (string) -- input string by the user
        word_list (list/tuple) -- list of extract_keywords_from_text

    Returns:
        (boolean) -- if keyword is found.
    """
    if word_list[0] == Config().DEFAULT_OTHERS:
        return True
    input_str = input_str.lower()
    return any([str(each) in str(input_str) for each in word_list])

def find_name(input_str):
    """
    A simple algorithm to extract names.

    Parameters:
        input_str(str) -- string containing the name
    """

    for each in ['i am', 'i\'m', 'this is', 'name is']:
        _index = input_str.lower().find(each)
        if _index != -1:
            result = input_str.lower()[_index + len(each)+1:]
            result = result.split()[0]
            for each_punc in list(string.punctuation):
                result = result.replace(each_punc,"")
            if len(result) > 0 and len(result) < 20:
                return result.capitalize()
    return input_str.capitalize().split()[0]



def find_problem(input_str):
    """
    Extract a candidate problem from an input string.

    Parameter:
        input_str(string) -- user input string

    Return:
        cand (string) -- candidate problem
    """
    r.extract_keywords_from_text(input_str)
    result = r.get_ranked_phrases()
    result = [''.join(c for c in s if c not in string.punctuation) for s in result]
    result = [s for s in result if (s and not s.endswith('ful'))]
    cand = None
    for keyword in result:
        tagged_list = [(token, pos) for token, pos in nltk.pos_tag(keyword.split()) if pos.startswith('N') or pos.startswith('V') or pos.startswith('J')]
        if len(tagged_list) == 0:
            continue
        tokens, poses = map(list, zip(*tagged_list))
        if not any([pos for pos in poses if pos.startswith('N')]):
            continue
        cand = ' '.join(tokens)
        break
    return cand

def detect_yes_no_dk(input_str):
    """
    Determine whether a string is yes, no, or unsure

    Parameter:
        input_str(string) -- user input string

    Return
        string -- either "yes" "no" or "dk" (don't know)
    """
    



