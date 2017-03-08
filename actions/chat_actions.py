import numpy as np
import telegram

import database.chat_db as chatdb
import database.rooms_db as roomdb
import database.subscription_db as sudb
import database.user_db as udb
import saver
from actions import super_actions


def forwmsg(bot, update):
    settings = super_actions.getBotSettings()
    for user in saver.getUsersToReply():
        if settings['duble_msgs'] or not user == update.message.from_user.id:
            try:
                bot.forward_message(user, from_chat_id=update.message.chat_id,
                                    message_id=update.message.message_id)
            except telegram.TelegramError as ex:
                print(ex.message)


def delAllNonSubs(bot, update):
    settings = super_actions.getBotSettings()
    all_subs = sudb.getAllSubs()
    for user in saver.getUsersToReply():
        if not user in all_subs:
            kickUser(bot, update, user)
            bot.sendMessage(user, text=settings['system_messages']['chat_is_paid'])


def newRoom(bot, update, hash=None):
    uid = update.message.from_user.id
    if saver.openPref(uid, 'room_name', hash) is None:
        super_actions.menu(bot, update)
    else:
        id = roomdb.appendRoom(saver.openPref(uid, 'room_name', None), hash)
        enterChat(bot, update, id)


def pickRoom(bot, update):
    rooms = roomdb.getAllRooms()
    settings = super_actions.getBotSettings()
    uid = update.message.from_user.id
    menu = np.array([])
    for room in rooms:
        menu = np.append(menu, room[1])
    menu = np.append(menu, super_actions.getKeyboard('room_browser', uid))
    keyboard = np.reshape(menu, (-1, 1))
    udb.setUserAction(update.message.from_user.id, 'room_browser')
    bot.sendMessage(update.message.chat_id, settings['system_messages']['pick_room'],
                    reply_markup=telegram.ReplyKeyboardMarkup(keyboard=keyboard))


def createRoom(bot, update):
    pay_options = super_actions.getPaySettings()
    settings = super_actions.getBotSettings()
    uid = update.message.from_user.id

    if pay_options["free"] is True or saver.isSubscriber(uid):
        udb.setUserAction(update.message.from_user.id, 'create_room')
        bot.sendMessage(update.message.chat_id, settings['create_room']['message'],
                        reply_markup=telegram.ReplyKeyboardMarkup(
                            keyboard=super_actions.getKeyboard('create_room', uid)))
    else:
        bot.sendMessage(uid, settings['system_messages']['not_sub_chat'])
        super_actions.pay(bot, update)


def enterPassword(bot, update):
    settings = super_actions.getBotSettings()
    uid = update.message.from_user.id
    udb.setUserAction(uid, 'enter_password')
    bot.sendMessage(uid, text=settings['enter_password']['message'],
                    reply_markup=telegram.ReplyKeyboardMarkup(
                        keyboard=super_actions.getKeyboard('enter_password', uid)))


def enterChat(bot, update, chat_id):
    pay_options = super_actions.getPaySettings()
    settings = super_actions.getBotSettings()
    uid = update.message.from_user.id
    if pay_options["free"] is True or saver.isSubscriber(uid):
        saver.addUserToChat(uid, chat_id)
        udb.setUserAction(uid, "chat")
        bot.sendMessage(uid, settings['system_messages']['in_chat'],
                        reply_markup=telegram.ReplyKeyboardMarkup(keyboard=super_actions.getKeyboard('chat', uid)))
        super_actions.sendmsg(bot, update, chatdb.getRoom(uid),
                              settings['system_messages']['user_entered'].format(udb.getFakeUserName(uid)))
    else:
        bot.sendMessage(uid, settings['system_messages']['not_sub_chat'])
        super_actions.pay(bot, update)


def leaveChat(bot, update):
    settings = super_actions.getBotSettings()
    uid = update.message.from_user.id
    if len(chatdb.getAllChaters(chatdb.getRoom(uid))) <= 1:
        roomdb.removeRoom(chatdb.getRoom(uid))
    else:
        super_actions.sendmsg(bot, update, chatdb.getRoom(uid),
                              settings['system_messages']['user_left'].format(udb.getFakeUserName(uid)))
    saver.kickUserFromChat(uid)
    super_actions.menu(bot, update)


def kickUser(bot, update, id):
    saver.kickUserFromChat(id)
    super_actions.menu(bot, update, id)
