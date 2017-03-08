import datetime
import hashlib
import time

import telegram

import database.subscription_db as sudb
import database.user_db as udb
import saver
from actions import chat_actions
from actions import super_actions, admin_actions
from database import admin_db as adb
from database import rooms_db as rooms


def getStatus(bot, update):
    settings = super_actions.getBotSettings()
    if sudb.getSubscriptionExpire(update.message.from_user.id) > 0:
        bot.sendMessage(update.message.chat_id, text=datetime.datetime.fromtimestamp(
            int(sudb.getSubscriptionExpire(update.message.from_user.id))).strftime('%Y-%m-%d'))
    else:
        bot.sendMessage(update.message.chat_id, text=settings['system_messages']['no_sub'])
        super_actions.pay(bot, update)


def performIt(bot, update, action):
    if action == 'menu':
        super_actions.menu(bot, update)
    elif action == 'pay':
        super_actions.pay(bot, update)
    elif action == 'create_room':
        chat_actions.createRoom(bot, update)
    elif action == 'change_nick':
        super_actions.changeNickname(bot, update)
    elif action == 'none_pass':
        chat_actions.newRoom(bot, update)
    elif action == 'status':
        getStatus(bot, update)
    elif action == 'room_browser':
        chat_actions.pickRoom(bot, update)
    elif action == 'give_sub':
        admin_actions.magic(bot, update, 'give_sub')
    elif action == 'leave_chat':
        chat_actions.leaveChat(bot, update)
    elif action == 'send_msg_chat':
        admin_actions.magic(bot, update, 'send_msg_chat')
    elif action == 'kick_user':
        admin_actions.magic(bot, update, 'kick_user')
    elif action == 'send_msg_all':
        admin_actions.magic(bot, update, 'send_msg_all')
    elif action == 'edit_prefs':
        admin_actions.editPrefs(bot, update)
    elif action == 'edit_price':
        admin_actions.editPrices(bot, update)
    elif action == 'add_admin':
        admin_actions.magic(bot, update, 'add_admin')
    elif action == 'del_admin':
        admin_actions.magic(bot, update, 'del_admin')
    elif action == 'contact_admin':
        super_actions.connect(bot, update)
    elif action == 'admin':
        admin_actions.magic(bot, update, 'admin_panel')




def answer(bot, update):
    settings = super_actions.getBotSettings()
    uid = update.message.from_user.id
    act = udb.getUserAction(update.message.from_user.id, settings['default_menu'])
    print(act)
    udb.setUserUsername(uid, update.message.from_user.username)
    if act in settings:
        for option in settings[act]['keyboard']:
            if option['text'] == update.message.text:
                performIt(bot, update, option['action'])
                return None

    if act == 'chat':
        if settings['message_every_min'] > 0 and not udb.getLastMsg(uid, 0) is None:
            if udb.getLastMsg(uid, 0) > 0 and time.time() - udb.getLastMsg(uid, 0) < settings['message_every_min'] * 60:
                bot.sendMessage(uid, text=settings['system_messages']['timeout'])
                return None
        super_actions.sendmsg(bot, update, rooms.getRoomID(uid))
        udb.setLatMsg(uid, time.time())
        return None
    elif act == 'enter_password':
        print(rooms.getRoomHash(saver.openPref(uid, 'room', -1)), '=',
              hashlib.sha256(update.message.text.encode('utf-8')).hexdigest())
        if rooms.getRoomHash(saver.openPref(uid, 'room', -1)) == \
                hashlib.sha256(update.message.text.encode('utf-8')).hexdigest():
            chat_actions.enterChat(bot, update, saver.openPref(uid, 'room', -1))
        else:
            chat_actions.enterPassword(bot, update)
    elif act == 'send_msg_chat':
        super_actions.sendmsg(bot, update, 0)
        admin_actions.magic(bot, update, 'admin_panel')
    elif act == 'change_nick':
        if udb.getFakeUserName(uid) == update.message.text:
            bot.sendMessage(chat_id=uid, text=settings['system_messages']['nick_not_available'])
            super_actions.changeNickname(bot, update)
        else:
            udb.setFakeUsername(uid, update.message.text)
            super_actions.menu(bot, update)
    elif act == 'create_password':
        chat_actions.newRoom(bot, update, hashlib.sha256(update.message.text.encode('utf-8')).hexdigest())

    elif act == 'create_room':
        if rooms.getRoomID(update.message.text):
            saver.savePref(uid, 'room_name', update.message.text)
            udb.setUserAction(uid, 'create_password')

            bot.sendMessage(uid, settings['create_password']['message'],
                            reply_markup=telegram.ReplyKeyboardMarkup(
                                keyboard=super_actions.getKeyboard('create_password', uid)))
    elif act == 'room_browser':
        room_id = rooms.getRoomID(update.message.text)
        if not room_id == -1:
            if rooms.getRoomHash(room_id):
                saver.savePref(uid, 'room', room_id)
                chat_actions.enterPassword(bot, update)
            else:
                chat_actions.enterChat(bot, update, room_id)
        else:
            bot.sendMessage(uid, text=settings['system_messages']['room_doesnt_exist'])
    elif act == 'send_msg_all':
        admin_actions.sendtoAll(bot, update, update.message.text)
        admin_actions.magic(bot, update, 'admin_panel')
    elif act == 'give_sub':
        if not udb.getID(update.message.text, -1) == -1:
            saver.addSubscription(udb.getID(update.message.text, -1), 0)
            admin_actions.magic(bot, update, 'admin_panel')
        else:
            bot.sendMessage(update.message.chat_id, text=settings['system_messages']['user_not_found'])
    elif act == 'kick_user':
        target = udb.getID(update.message.text, -1)
        if not target == -1:
            sudb.removeSubscriber(target)
            chat_actions.kickUser(bot, update, target)
            admin_actions.magic(bot, update, 'admin_panel')
            bot.sendMessage(target, text=settings['system_messages']['user_kicked'])
        else:
            bot.sendMessage(update.message.chat_id, text=settings['system_messages']['user_not_found'])
    elif act == 'edit_prefs':
        super_actions.replaceSettings(bot, update, 'bot')
    elif act == 'add_admin':
        adb.appendAdmin(int(update.message.text))
        admin_actions.magic(bot, update, 'admin_panel')
    elif act == 'del_admin':
        adb.removeAdmin(int(update.message.text))
        admin_actions.magic(bot, update, 'admin_panel')
    elif act == 'edit_price':
        super_actions.replaceSettings(bot, update, 'subscriptions')
        if not super_actions.getPaySettings()['free']:
            chat_actions.delAllNonSubs(bot, update)



