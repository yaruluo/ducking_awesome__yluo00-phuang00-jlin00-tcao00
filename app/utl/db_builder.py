import sqlite3

DB_FILE = "journal.db"

#==========================================================
# EXEC COMMANDS

def exec(cmd):
    """Executes a sqlite command"""
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd)
    db.commit()
    return output

def execmany(cmd, inputs):
    """Executes a sqlite command using ? placeholder"""
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    output = c.execute(cmd, inputs)
    db.commit()
    return output

#==========================================================
# BUILD DATABASE

def build_db():
    """Creates database if it does not yet exist with the necessary tables"""
    command = "CREATE TABLE IF NOT EXISTS user_tbl (user_id INT, username TEXT, password TEXT, mood TEXT, sleep TEXT, period TEXT, permission INT, friends TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS journal_tbl (entry_id INT, user_id INT, date DATETIME, body TEXT, tdlist TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS comment_tbl (entry_id INT, commenter_id INT, comment TEXT)"
    exec(command)
