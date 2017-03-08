import sqlite3

# Database name
filename = "data"

# User table name
rooms_table_name = "rooms"

# User table generate request
rooms_generate = "create table if not exists " + rooms_table_name + \
                 " (id integer PRIMARY KEY, name text, password_hash text)"

remove_room = "DELETE FROM " + rooms_table_name + " WHERE id = ?"
get_everything = "SELECT * FROM " + rooms_table_name
get_id = "SELECT id FROM " + rooms_table_name + " WHERE name = ?"
get_hash = "SELECT password_hash FROM " + rooms_table_name + " WHERE id = ?"


def getAllRooms():
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_everything)
    wet_data = c.fetchall()
    print(wet_data)
    return wet_data


def getRoomID(name):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_id, [name])
    id = c.fetchone()
    conn.commit()
    conn.close()
    if id is None:
        return -1
    else:
        return id[0]


def getRoomHash(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(get_hash, [id])
    hash = c.fetchone()
    conn.commit()
    conn.close()
    if hash is None:
        return None
    else:
        return hash[0]


def removeRoom(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(remove_room, [id])
    conn.commit()
    conn.close()


def appendRoom(name, hash):
    if getRoomID(name) == -1:
        conn = sqlite3.connect(filename + '.db')
        c = conn.cursor()
        admin_update = "insert or ignore INTO " + rooms_table_name + "(name, password_hash) VALUES (?, ?);"
        c.execute(admin_update, [name, hash])
        conn.commit()
        conn.close()
        return getRoomID(name)


def initDB(file):
    global filename
    filename = file
    conn = sqlite3.connect(file + ".db")
    c = conn.cursor()
    c.execute(rooms_generate)
    conn.commit()
    conn.close()
