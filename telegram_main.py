#/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
telegram_main.py  -- v2
---------------------------------------------------------------
        

        USE THIS FILE TO RUN THE PROGRAM



This file is contains the main funtion for the Telegram implementation.

Funtions in this file will communicate with the Telegram API,
and make calls to the database file.

Created by Nick Tantivasadakarn.
"""
import telegram 
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
from state_handler import StateHandler
import os

from telegram.ext.dispatcher import run_async


class TelegramPopBots():
    def __init__(self, bot_folder):
        self.bot_folder = bot_folder
        self.state_handler = StateHandler(bot_folder)


    @run_async
    def callback_queue(self, bot, job):
        """
        (Invoked by callback_handler)
        This fucntion will process the user input 
        """
        #try:
        message, buttons = self.state_handler.get_response(job.context.chat_id, job.context.text)

        reply_markup = self.create_reply_markup(buttons)
        for m in message:
            if isinstance(m, str): #handle text
                bot.send_message(chat_id=job.context.chat_id, text=m, reply_markup = reply_markup)
            
            elif isinstance(m, dict):
                if 'img' in m: #handle images
                    path = os.path.join(self.bot_folder,m['img'])
                    img = open(path, 'rb')
                    bot.send_photo(chat_id=job.context.chat_id, photo=img, reply_markup = reply_markup)
        # except:
        #     bot.send_message(chat_id=job.context.chat_id, 
        #         text="Opps! There seems to be an error. Please contact the researcher and report this problem.")

    def callback_handler(self, bot, update, job_queue):
        """
        This is a callback functiona that is invoked after a message is sent from the user.
        It will sent a message after a set (2 second) delay.

        """
        job_queue.run_once(self.callback_queue, 1, context=update.message)


    def create_reply_markup(self, buttons):
        """
        Creates buttons (a.k.a custom keyboard)
        if there are not buttons it will remove the keyboard. 

        Parameters:
            button (list or list of lists) -- the keyboard 

        Note a list will organize the buttons vertically while a 
        list of list will be horizontal. You can mix the two as well
        """
        if buttons:
            button_list = []
            for rows in buttons:
                if isinstance(rows, list):
                    row = []
                    for col in rows:
                        row.append(telegram.InlineKeyboardButton(col))
                    button_list.append(row)

                else:
                    button_list.append([telegram.InlineKeyboardButton(rows)])
            return telegram.ReplyKeyboardMarkup(button_list)
        else:
            reply_markup = telegram.ReplyKeyboardRemove()


    def run(self, token):
        updater = Updater(token)
        dp = updater.dispatcher # Get the dispatcher to register handlers
        handler = MessageHandler(Filters.text, self.callback_handler, pass_job_queue=True)
        dp.add_handler(handler)
        print ("running bot")
        updater.start_polling()


if __name__ == '__main__':
    # Telegram Bot Authorization Token
    #main('676639758:AAFrOKaCJAzBOO-7LM2W3p4Ie1Rkf9O6qsU')
    bot = TelegramPopBots('./example_bots')
    bot.run('660721089:AAFFtzkiZVC96U_Cqzt3Y3sW_BsHaFyJfFY') #bot for testing only