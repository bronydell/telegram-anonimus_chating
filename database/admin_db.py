import sqlite3

# Database name
filename = "data"

# User table name
admin_table_name = "admin"

# User table generate request
admin_generate = "create table if not exists " + admin_table_name + \
                 " (id integer PRIMARY KEY, muted integer)"

remove_admin = "DELETE FROM " + admin_table_name + " WHERE id = ?"
get_everything = "SELECT id FROM " + admin_table_name

def getAllAdmins():
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

def appendAdmin(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    # Insert or replace action for user
    admin_update = "update " + admin_table_name + " SET id = ? WHERE id = ?;"
    c.execute(admin_update, [id, id])
    # If not succeed
    admin_update = "insert or ignore INTO " + admin_table_name + "(id) VALUES (?);"
    c.execute(admin_update, [id])
    conn.commit()
    conn.close()

def removeAdmin(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute(remove_admin, [id])
    conn.commit()
    conn.close()

def muteUser(id):
    conn = sqlite3.connect(filename + '.db')
    c = conn.cursor()
    c.execute("update " + admin_table_name + " SET id = ? WHERE id = ?;", [id])
    conn.commit()
    conn.close()

def initDB(file):
    global filename
    filename = file
    conn = sqlite3.connect(file + ".db")
    c = conn.cursor()
    c.execute(admin_generate)
    conn.commit()
    conn.close()