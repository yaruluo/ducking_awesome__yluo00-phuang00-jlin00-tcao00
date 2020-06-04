import sqlite3
from utl.db_builder import exec, execmany
import random, sys

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
        #assign unique user_id
        q = "SELECT user_id FROM user_tbl"
        data = exec(q).fetchall()
        user_id = random.randrange(limit)
        while (user_id in data):
            user_id = random.randrange(limit)

        #add entry into user table
        q = "INSERT INTO user_tbl VALUES(?, ?, ?, '', '', '', 0, '', '')"
        inputs = (user_id, username, password)
        execmany(q, inputs)
        return True
    return False #if username already exists

def changePass(username, password):
    '''def changePass(username, password): updating data table of user in session with new password'''
    q = "UPDATE user_tbl SET password=? WHERE username=?"
    inputs = (password, username)
    execmany(q, inputs)

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
