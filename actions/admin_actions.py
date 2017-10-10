from actions import super_actions
from database import user_db as udb
import telegram
import saver
import numpy as np

def sendtoAll(bot, update, txt):
    settings = super_actions.getBotSettings()
    if saver.isAdmin(update.message.from_user.id):
        for user in udb.getAllUsers():
            try:
                bot.sendMessage(user, text=txt)
            except telegram.TelegramError as ex:

                pass
    else:
        bot.sendMessage(update.message.chat_id, text=settings['system_messages']['not_admin'])


def magic(bot, update, act):
    settings = super_actions.getBotSettings()
    if saver.isAdmin(update.message.from_user.id):
        uid = update.message.from_user.id
        udb.setUserAction(uid, act)
        bot.sendMessage(update.message.chat_id, text=settings[act]['message'],
                        reply_markup=telegram.ReplyKeyboardMarkup(keyboard=super_actions.getKeyboard(act, uid)))
    else:
        bot.sendMessage(update.message.chat_id, text=settings['system_messages']['not_admin'])

def editPrices(bot, update):
    settings = super_actions.getBotSettings()
    if saver.isAdmin(update.message.from_user.id):
        uid = update.message.from_user.id
        act = 'edit_price'
        udb.setUserAction(uid, act)
        bot.sendMessage(update.message.chat_id, text=settings[act]['message'],
                        reply_markup=telegram.ReplyKeyboardMarkup(keyboard=super_actions.getKeyboard(act, uid)))
        bot.sendDocument(update.message.chat_id, document=open('subscriptions.json', 'rb'))
    else:
        bot.sendMessage(update.message.chat_id, text=settings['system_messages']['not_admin'])

def editPrefs(bot, update):
    settings = super_actions.getBotSettings()
    if saver.isAdmin(update.message.from_user.id):
        uid = update.message.from_user.id
        act = 'edit_prefs'
        udb.setUserAction(uid, act)
        bot.sendMessage(update.message.chat_id, text=settings[act]['message'],
                        reply_markup=telegram.ReplyKeyboardMarkup(keyboard=super_actions.getKeyboard(act, uid)))
        bot.sendDocument(update.message.chat_id, document=open('bot.json', 'rb'))
    else:
        bot.sendMessage(update.message.chat_id, text=settings['system_messages']['not_admin'])
