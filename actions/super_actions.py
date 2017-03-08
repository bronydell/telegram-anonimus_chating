import datetime
import json
import time
from shutil import move

import numpy as np
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import database.chat_db as chatdb
import database.rooms_db as roomdb
import database.subscription_db as sudb
import database.user_db as udb
import saver
from actions import admin_actions


def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError:
    return False
  return True


def sendmsg(bot, update, room_id, text=None):
    settings = getBotSettings()
    for user in saver.getUsersToReply(room_id):
        if settings['duble_msgs'] or not user == update.message.from_user.id:
            sendMessage(bot, update, user, text)


def sendMessage(bot, update, user, text=None):
    settings = getBotSettings()
    uid = update.message.from_user.id
    message = update.message
    if text is None:
        try:

            if message.reply_to_message:
                bot.forward_message(user, from_chat_id=message.reply_to_message.chat.id,
                                    message_id=message.reply_to_message.message_id)
            if message.photo:
                if message.caption:
                    bot.sendPhoto(chat_id=user, photo=message.photo[-1].file_id, caption=
                    settings['templates']['text_message'].format(udb.getFakeUserName(uid), message.caption))
                else:
                    bot.sendPhoto(chat_id=user, photo=message.photo[-1].file_id, caption=
                    settings['templates']['photo_message'].format(udb.getFakeUserName(uid)))
            elif message.text:
                bot.sendMessage(chat_id=user, text=settings['templates']['text_message'].
                                format(udb.getFakeUserName(uid), message.text))
            elif message.document:
                if message.caption:
                    bot.sendDocument(chat_id=user, document=message.document.file_id, caption=
                    settings['templates']['text_message'].format(udb.getFakeUserName(uid), message.caption))
                else:
                    bot.sendDocument(chat_id=user, document=message.document.file_id, caption=
                    settings['templates']['document_message'].format(udb.getFakeUserName(uid)))
            elif message.sticker:
                bot.sendSticker(chat_id=user, sticker=message.sticker.file_id)
            elif message.voice:
                if message.caption:
                    bot.sendVoice(chat_id=user, voice=message.voice.file_id, caption=
                    settings['templates']['text_message'].format(udb.getFakeUserName(uid), message.caption))
                else:
                    bot.sendVoice(chat_id=user, voice=message.voice.file_id, caption=
                    settings['templates']['voice_message'].format(udb.getFakeUserName(uid)))
            elif message.audio:
                if message.caption:
                    bot.sendAudio(chat_id=user, audio=message.audio.file_id, caption=
                    settings['templates']['text_message'].format(udb.getFakeUserName(uid), message.caption))
                else:
                    bot.sendAudio(chat_id=user, audio=message.audio.file_id, caption=
                    settings['templates']['audio_message'].format(udb.getFakeUserName(uid)))
            elif message.video:
                if message.caption:
                    bot.sendVideo(chat_id=user, video=message.video.file_id, caption=
                    settings['templates']['text_message'].format(udb.getFakeUserName(uid), message.caption))
                else:
                    bot.sendVideo(chat_id=user, video=message.video.file_id, caption=
                    settings['templates']['video_message'].format(udb.getFakeUserName(uid)))

        except telegram.TelegramError as ex:
            bot.sendMessage(update.message.from_user.id, text='Произошла ошибка: ' + str(ex.message))
    else:
        bot.sendMessage(chat_id=user, text=text)

def replaceSettings(bot, update, filename):
    settings = getBotSettings()
    if update.message.document:
        move(filename+'.json', filename+'_old'+'.json')
        file_id = update.message.document.file_id
        bot.getFile(file_id).download(filename+'.json')
        with open(filename+'.json', 'r') as content_file:
            if not is_json(content_file.read()):
                move(filename+'_old'+'.json', filename+'.json')
                bot.sendMessage(update.message.chat_id, text=settings['system_messages']['json_bot_not_valid'])
            else:
                bot.sendMessage(update.message.chat_id, text=settings['system_messages']['json_bot_valid'])
                admin_actions.magic(bot, update, 'admin_panel')

def getKeyboard(tag, id):
    settings = getBotSettings()
    menu = np.array([])
    for option in settings[tag]['keyboard']:
        if isFree() and 'show_when_free' in option:
            if not option['show_when_free']:
                continue
        if 'admin_only' in option:
            if saver.isAdmin(id) or option['admin_only'] == False:
                menu = np.append(menu, option['text'])
        else:
            menu = np.append(menu, option['text'])
    return np.reshape(menu, (-1, 1))

def getBotSettings():
    with open('bot.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data


def getPaySettings():
    with open('subscriptions.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data

def controlSubs(bot, job):
    settings = getBotSettings()
    subs = sudb.getAllSubs()
    for sub in subs:
        notify = datetime.datetime.fromtimestamp(int(time.time()))
        now = datetime.datetime.fromtimestamp(int(sudb.getSubscriptionExpire(sub)))
        delta = now - notify
        dayz = delta.days + 1
        if sudb.getSubscriptionExpire(sub) < time.time():
            sudb.removeSubscriber(sub)
            bot.sendMessage(chat_id=sub,
                                    text=settings['system_messages']['out_of_sub'])
            return None
        if sudb.getSubscriptionNotify(sub) > time.time():
            if dayz == 3:
                sudb.setNotify(sub, sudb.getSubscriptionNotify(sub)+60*60*24)
                bot.sendMessage(chat_id=sub,
                                    text=settings['system_messages']['3days_left'])
                pay(bot, None, sub)
            if dayz == 2:
                sudb.setNotify(sub, sudb.getSubscriptionNotify(sub)+60*60*24)
                bot.sendMessage(chat_id=sub,
                                    text=settings['system_messages']['2days_left'])
                pay(bot, None, sub)
            if dayz <= 1:
                sudb.setNotify(sub, sudb.getSubscriptionNotify(sub)+60*60*24)
                bot.sendMessage(chat_id=sub,
                                    text=settings['system_messages']['1days_left'])
                pay(bot, None, sub)

def connect(bot, update):
    settings = getBotSettings()
    uid = update.message.from_user.id
    bot.sendMessage(uid, text=settings['system_messages']['admin_info'])

def menu(bot, update, id = -1):
    settings = getBotSettings()
    uid = update.message.from_user.id
    if not id == -1:
        uid = id

    if len(chatdb.getAllChaters(chatdb.getRoom(uid))) <= 1:
        roomdb.removeRoom(chatdb.getRoom(uid))
    else:
        sendmsg(bot, update, chatdb.getRoom(uid),
                settings['system_messages']['user_left'].format(udb.getFakeUserName(uid)))
    saver.kickUserFromChat(uid)
    act = 'menu'
    udb.setUserAction(uid, settings['default_menu'])
    udb.setUserUsername(uid, update.message.from_user.username)
    bot.sendMessage(uid, text=settings[act]['message'],
                    reply_markup=telegram.ReplyKeyboardMarkup(keyboard=getKeyboard(act, uid)))


def changeNickname(bot, update):
    settings = getBotSettings()
    uid = update.message.from_user.id
    act = 'change_nick'
    udb.setUserAction(uid, act)
    udb.setUserUsername(uid, update.message.from_user.username)
    bot.sendMessage(uid, text=settings[act]['message'],
                    reply_markup=telegram.ReplyKeyboardMarkup(keyboard=getKeyboard(act, uid)))


def isFree():
    return getPaySettings()["free"]

def pay(bot, update, id = -1):
    if not update is None:
        uid = update.message.from_user.id
    pay_options = getPaySettings()
    settings = getBotSettings()
    pay_types = np.array([])
    if not id == -1:
        uid = id
    type = 0
    for option in pay_options['types']:
        if sudb.getSubscriptionExpire(uid) > 0:
            pay_types = np.append(pay_types,
                                  InlineKeyboardButton(text=option['have_it'],
                                                       url=settings['domain'] + '/pay.php?u=' + str(uid)
                                                           + '&type=' + str(type)))
        else:
            pay_types = np.append(pay_types,
                                  InlineKeyboardButton(text=option['buy_it'],
                                                       url=settings['domain'] + '/pay.php?u=' + str(uid)
                                                           + '&type=' + str(type)))
        type += 1
    bot.sendMessage(uid, text=settings['system_messages']['pay_message'],
                    reply_markup=InlineKeyboardMarkup(np.reshape(pay_types, (-1, 1))))

