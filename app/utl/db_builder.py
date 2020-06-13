# standard library imports
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
    command = "CREATE TABLE IF NOT EXISTS user_tbl (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, permissions INT, friends TEXT, requests TEXT, newlists TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS journal_tbl (entry_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, date DATETIME, body TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS tdlist_tbl (entry_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, date DATETIME, task TEXT, description TEXT, time TEXT, resolved INT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS comment_tbl (entry_id INT, comment_id INTEGER PRIMARY KEY AUTOINCREMENT, commenter_id INT, comment TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS mood_tbl (user_id INTEGER, date TEXT, mood INTEGER)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS sleep_tbl (user_id INTEGER, date TEXT, sleep REAL)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS future_tbl (user_id INTEGER, list_id INTEGER PRIMARY KEY AUTOINCREMENT, type INTEGER, title TEXT, items TEXT, collaborators TEXT)"
    exec(command)

    command = "CREATE TABLE IF NOT EXISTS listitem_tbl (item_id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, resolved INT)"
    exec(command)
