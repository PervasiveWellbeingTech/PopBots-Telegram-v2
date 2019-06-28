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

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
from state_handler import StateHandler
import os


class TelegramBot():
    def __init__(self, bot_folder):
        self.bot_folder = bot_folder
        self.state_handler = StateHandler(bot_folder)


    def callback_queue(self, bot, job):
        """
        (Invoked by callback_handler)
        This fucntion will process the user input 
        """
        try:
            message = self.state_handler.get_response(job.context.chat_id, job.context.text)
            for m in message:
                if isinstance(m, str): #handle text
                    bot.send_message(chat_id=job.context.chat_id, text=m)
                
                elif isinstance(m, dict):
                    
                    if 'img' in m: #handle images
                        path = os.path.join(self.bot_folder,m['img'])
                        img = open(path, 'rb')
                        bot.send_photo(chat_id=job.context.chat_id, photo=img)
        except:
            bot.send_message(chat_id=job.context.chat_id, 
                text="Opps! There seems to be an error. Please contact the researcher and report this problem.")

    def callback_handler(self, bot, update, job_queue):
        """
        This is a callback functiona that is invoked after a message is sent from the user.
        It will sent a message after a set (2 second) delay.

        """
        job_queue.run_once(self.callback_queue, 2, context=update.message)

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
    bot = TelegramBot('./shallow_bots')
    bot.run('660721089:AAFFtzkiZVC96U_Cqzt3Y3sW_BsHaFyJfFY') #bot for testing only