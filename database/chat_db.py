import sqlite3

# Database name
filename = "data"

# User table name
chat_table_name = "chat"

# User table generate request
chat_generate = "create table if not exists " + chat_table_name + \
                " (id integer PRIMARY KEY, room id, muted integer)"

remove_user = "DELETE FROM " + chat_table_name + " WHERE id = ?"
get_by_id = "SELECT id FROM " + chat_table_name + " WHERE room = ?"
get_everything = "SELECT id FROM " + chat_table_name
get_room = "SELECT room FROM " + chat_table_name + " WHERE id = ?"


def getRoom(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_room, [id])
    data = c.fetchone()
    conn.commit()
    conn.close()
    if data is None:
        return None
    return data[0]


def getAllChaters(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    if id == -1:
        c.execute(get_everything)
    else:
        c.execute(get_by_id, [id])
    wet_data = c.fetchall()
    users = []
    for user in wet_data:
        users+=user
    conn.commit()
    conn.close()
    return users


def appendUser(id, chat_id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    # Insert or replace action for user
    username_update = "update " + chat_table_name + " SET id = ?, room = ? WHERE id = ?;"
    c.execute(username_update, [id, chat_id, id])
    # If not succeed
    username_update = "insert or ignore INTO " + chat_table_name + "(id, room) VALUES (?, ?);"
    c.execute(username_update, [id, chat_id])
    conn.commit()
    conn.close()

def kickUser(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(remove_user, [id])
    conn.commit()
    conn.close()

def muteUser(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute("update " + chat_table_name + " SET id = ? WHERE id = ?;", [id, id])
    conn.commit()
    conn.close()

def initDB(file):
    global filename
    filename = file
    conn = sqlite3.connect(file + ".db")
    c = conn.cursor()
    c.execute(chat_generate)
    conn.commit()
    conn.close()