import sqlite3
from utl.db_builder import exec, execmany
import random, sys
from datetime import datetime

limit = sys.maxsize
#====================================================
# LOGIN FUNCTIONS

def userValid(username, password):
    '''def userValid(username,password): determines if username is in database and password corresponds to username'''
    q = "SELECT username FROM user_tbl;"
    data = exec(q)
    for uName in data:
        if uName[0] == username:
            q = "SELECT password from user_tbl WHERE username=?"
            inputs = (username,)
            data = execmany(q, inputs)
            for passW in data:
                if (passW[0] == password):
                    return True
    return False

def addUser(username, password):
    '''def addUser(username, password): adding user from sign up,
    taking in form inputs and writing to data table'''
    q = "SELECT * FROM user_tbl WHERE username=?"
    inputs = (username,)
    data = execmany(q, inputs).fetchone()
    if (data is None):
        #add entry into user table
        q = "INSERT INTO user_tbl (username, password, permissions) VALUES(?, ?, ?)"
        inputs = (username, password, 0)
        execmany(q, inputs)
        return True
    return False #if username already exists

def changePass(username, password):
    '''def changePass(username, password): updating data table of user in session with new password'''
    q = "UPDATE user_tbl SET password=? WHERE username=?"
    inputs = (password, username)
    execmany(q, inputs)

def getUserID(username):
    q = "SELECT user_id FROM user_tbl WHERE username=?"
    inputs = (username,)
    id = execmany(q, inputs).fetchone()[0]
    print(id)
    return id

#====================================================
# MANAGING FRIENDS

def getPermissions(username):
    '''def getPermissions(username): get user's permissions and convert into a dictionary'''
    q = "SELECT permissions FROM user_tbl WHERE username=?"
    inputs = (username,)
    data = execmany(q, inputs).fetchone()[0]
    print(data)
    dict = {0: [False, "View Journals"], 1: [False, "View Mood Tracker"],
            2: [False, "View Sleep Tracker"], 3: [False, "View Period Tracker"],
            4: [False, "View To-Do Lists"], 5: [False, "Comment Access"]}
    for i in range(6):
        index = 5 - i
        quotient = data // pow(10, index)
        if (quotient != 0):
            dict[index][0] = True
        data = data % pow(10, index)
    return dict

#====================================================
# MANAGING JOURNAL ENTRIES

def updateEntry(username, entry):
    '''def updateEntry(username, entry): add a new entry to the journal_tbl'''
    idNum = getUserID(username)
    q = "SELECT body FROM journal_tbl WHERE user_id=? AND date=?"
    today = datetime.now()
    date = today.date()
    inputs = (idNum, date)
    data = execmany(q, inputs).fetchone()
    print(data)
    if(data is None):
        print("nope")
        q = "INSERT INTO journal_tbl (user_id, date, body) VALUES(?, ?, ?)"
        inputs = (idNum, date, entry)
        execmany(q, inputs)
    else:
        print("yup")
        q = "UPDATE journal_tbl SET body=? WHERE user_id=? AND date=?"
        inputs = (entry, idNum, date)
        execmany(q, inputs)


def getEntry(username, date):
    '''def getEntry(username, date): retrieve the body text of the user at the specified date'''
    idNum = getUserID(username)
    q = "SELECT body FROM journal_tbl WHERE user_id=? AND date=?"
    inputs = (idNum, date)
    data = execmany(q, inputs).fetchone()
    print(data)
    return data

def addMood(user_id, date, mood):
    '''adds the mood into the mood table if it does not already exist,
       updates the mood if there is already a value inputed for the day'''
    if getMood(user_id, date) is None:
        q = "INSERT INTO mood_tbl VALUES(?, ?, ?)"
        inputs = (user_id, date, mood)
        execmany(q, inputs)
    else:
        q = "UPDATE mood_tbl SET mood = ? WHERE user_id = ? AND date = ?"
        inputs = (mood, user_id, date)
        execmany(q, inputs)

def getMood(user_id, date):
    '''returns the mood for the given date and user'''
    q = "SELECT mood FROM mood_tbl WHERE user_id = ? AND date = ?"
    inputs = (user_id, date,)
    data = execmany(q, inputs).fetchone()
    if data is None:
        return data
    else:
        return data[0]

def getMonthMoods(user_id, month_year):
    '''returns a list of all the moods in the given month for the given user in the format:
        [{'date': <date>, 'mood': <mood>}, ... ]
    '''
    q = "SELECT date, mood FROM mood_tbl WHERE user_id = ? AND date LIKE ?"
    inputs = (user_id, month_year + '%',)
    data = execmany(q, inputs)
    dict = []
    for row in data:
        dict.append({'date': row[0], 'mood': row[1]})
    return dict
