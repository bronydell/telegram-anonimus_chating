import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


import answers
import saver
from actions import super_actions
from database import admin_db

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                  level=logging.DEBUG)


def error_callback(bot, update, error):

    print(bot.token)

with open('key.config', 'r', encoding='utf-8') as myfile:
    key = myfile.read().replace('\n', '')


updater = Updater(key)
saver.initDataBase()

if len(admin_db.getAllAdmins()) <= 0:
    admin_id = input("Введите Telegram ID администратора: ")
    admin_db.appendAdmin(admin_id)

j = updater.job_queue
job_minute = Job(super_actions.controlSubs, 60*60*24)
j.put(job_minute, next_t=0.0)
updater.dispatcher.add_error_handler(error_callback)
updater.dispatcher.add_handler(MessageHandler(Filters.document | Filters.text | Filters.photo | Filters.audio
                                              | Filters.sticker | Filters.voice | Filters.video,
                                              answers.answer))
updater.dispatcher.add_handler(CommandHandler('start', super_actions.menu))
updater.dispatcher.add_handler(CommandHandler('cancel', super_actions.menu))

updater.start_polling()
updater.idle()