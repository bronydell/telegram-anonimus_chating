import json
import os
import shelve
import sqlite3
import sys
import time

import telegram

import database.admin_db as admindb
import database.chat_db as chat
import database.rooms_db as roomdb
import database.subscription_db as subdb
import database.user_db as udb
import model.subscriber as Subsriber

shelve_name = "settings"


def savePref(user, key, value):
    d = shelve.open(shelve_name)
    d[str(user) + '.' + str(key)] = value
    d.close()


def openPref(user, key, default):
    d = shelve.open(shelve_name)
    if (str(user) + '.' + str(key)) in d:
        return d[str(user) + '.' + str(key)]
    else:
        return default

def getPricing():
    with open('subscriptions.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def addUserToChat(id, chat_id):
    chat.appendUser(id, chat_id)

def kickUserFromChat(id):
    chat.kickUser(id)



def muteUser(id):
    udb.setMuted(id, not udb.isMuted(id))

def isSubscriber(id):
    if subdb.getSubscriptionExpire(id) > time.time():
        return True
    return False


def isAdmin(id):
    if id in admindb.getAllAdmins():
        return True
    return False


def getUsersToReply(id=-1):
    return chat.getAllChaters(id)

def initDataBase():
    filename = "data"
    conn = sqlite3.connect(filename + ".db")
    c = conn.cursor()

    # Create tables
    subdb.initDB(filename)
    udb.initDB(filename)
    chat.initDB(filename)
    admindb.initDB(filename)
    roomdb.initDB(filename)
    conn.commit()
    conn.close()

def addSubscription(user_id, type):
    info = getPricing()['types'][type]
    sub = Subsriber.Subscriber(user_id, 0)
    with open('key.config', 'r', encoding='utf-8') as myfile:
        key = myfile.read().replace('\n', '')
    if subdb.getSubscriptionExpire(user_id) > time.time():
        subdb.setSubscriber(sub, subdb.getSubscriptionExpire(user_id)+info['days'] * 24 * 60 * 60)
        telegram.Bot(token=key).send_message(user_id, info['success_again'])
    else:
        subdb.setSubscriber(sub, time.time()+info['days'] * 24 * 60 * 60)
        telegram.Bot(token=key).send_message(user_id, info['success'])


if __name__ == "__main__":
    type = int(sys.argv[2])
    uid = int(sys.argv[1])
    addSubscription(uid, type)