import sqlite3
import os
import sys

# Database name
filename = "data"

# Month
mouth = 60 * 60 * 24 * 31
# Week
week = 60 * 60 * 24 * 7

# Table name
table_name = "subscription"

# Subscribers table generate request
users_generate = "create table if not exists " + table_name + \
                 " (id integer PRIMARY KEY, expire integer, notify integer)"

delete_subscriber = "DELETE FROM " + table_name + " WHERE id = ?"

get_all_expire_time = "SELECT id FROM "+table_name

get_all_notify = "SELECT id FROM "+table_name+" WHERE notify = 1"

get_subscriber_expire = "SELECT expire FROM "+table_name+" WHERE id = ?"

get_subscriber_notify = "SELECT expire FROM "+table_name+" WHERE id = ?"

get_everything = "SELECT id FROM " + table_name

def getAllSubs():
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_everything)
    wet_data = c.fetchall()
    users = []
    for user in wet_data:
        users += user
    conn.commit()
    conn.close()
    return users

def setSubscriber(subscriber, expire):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    notify = expire - 60 * 60 * 24 * 3
    # Insert or replace action for user
    if getSubscriptionExpire(subscriber.getID()) > 0:
        subscriber_update = "update " + table_name + " SET id = ?,  expire = ?, notify = ? WHERE id = ?;"
        params = (subscriber.getID(),  expire, notify, subscriber.getID())
        c.execute(subscriber_update, params)
    else:
        params = (subscriber.getID(), expire, notify)
        subscriber_update = "insert or ignore INTO " + table_name + "(id, expire, notify) VALUES (?, ?, ?);"
        c.execute(subscriber_update, params)
    conn.commit()
    conn.close()

def setNotify(id, notify):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute("update " + table_name + " SET notify = ? WHERE id = ?;", [notify, id])
    conn.commit()
    conn.close()

def removeSubscriber(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(delete_subscriber, [id])
    conn.commit()
    conn.close()

def getSubscribers():
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_all_expire_time)
    expire = c.fetchall()
    conn.commit()
    conn.close()
    return expire

def getSubscriptionExpire(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_subscriber_expire, [id])
    expire = c.fetchone()
    conn.commit()
    conn.close()
    if (expire is not None) and (expire[0] is not None):
        return int(expire[0])
    else:
        return 0

def getSubscriptionNotify(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_subscriber_expire, [id])
    notify = c.fetchone()
    conn.commit()
    conn.close()
    if (notify is not None) and (notify[0] is not None):
        return int(notify[0])
    else:
        return 0

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def initDB(file):
    global filename
    filename = file
    conn = sqlite3.connect(file + ".db")
    c = conn.cursor()
    # Create table
    c.execute(users_generate)
    conn.commit()
    conn.close()