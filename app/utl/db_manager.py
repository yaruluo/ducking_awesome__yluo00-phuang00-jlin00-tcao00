import sqlite3
from utl.db_builder import exec, execmany
import random, sys
from datetime import datetime
import json

limit = sys.maxsize
MOOD_DICT = {0: ['happy/joyful/content/relax', '#ffb6e6'], 1: ['sad/lonely/depressed/insecure', '#a3dbff'],
             2: ['productive/motivated/alive/excited', '#71ffda'], 3: ['sick/tired/bored/lazy', '#feffb2'],
             4: ['average/normal/fine/OK', '#ffd177'], 5: ['angry/anxious/fustrated/annoyed', '#ff5b5b']}
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

def changePass(user_id, password):
    '''def changePass(username, password): updating data table of user in session with new password'''
    q = "UPDATE user_tbl SET password=? WHERE user_id=?"
    inputs = (password, user_id)
    execmany(q, inputs)

def getUserID(username):
    '''def getUserID(username): return user_id for given username'''
    q = "SELECT user_id FROM user_tbl WHERE username=?"
    inputs = (username,)
    id = execmany(q, inputs).fetchone()[0]
    return id

def getUsername(user_id):
    '''def getUsername(user_id): return username for given user_id'''
    q = "select username FROM user_tbl WHERE user_id=?"
    inputs = (user_id, )
    data = execmany(q, inputs).fetchone()[0]
    return data

#====================================================
# MANAGING FRIENDS

def getPermissions(user_id):
    '''def getPermissions(user_id): get user's permissions and convert into a dictionary'''
    q = "SELECT permissions FROM user_tbl WHERE user_id=?"
    inputs = (user_id,)
    data = execmany(q, inputs).fetchone()[0]
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

def updatePermissions(user_id, permissions):
    '''def updatePermissions(user_id): set user's permissions'''
    q = "UPDATE user_tbl SET permissions=? WHERE user_id=?"
    inputs = (permissions, user_id)
    execmany(q, inputs)

def getFriends(user_id):
    '''def getFriends(user_id): get user list of friends'''
    q = "SELECT friends FROM user_tbl WHERE user_id=?"
    inputs = (user_id, )
    data = execmany(q, inputs).fetchone()[0]
    if data is None:
        return []
    return data.split(",")

def formatFriends(user_id):
    '''formatFriends(user_id): formats user's list of friends'''
    friends = getFriends(user_id)
    list = []
    for friend in friends:
        info = []
        info.append(getUsername(friend))
        info.append(friend)
        list.append(tuple(info))
    return list

def getRequests(user_id):
    '''getRequests(user_id): get list of requests sent to user'''
    q = "SELECT requests FROM user_tbl WHERE user_id=?"
    inputs = (user_id, )
    data = execmany(q, inputs).fetchone()[0]
    if data is None:
        return []
    return data.split(",")

def formatRequests(user_id):
    '''formatRequests(user_id): formats lists of requests sent to user'''
    requests = getRequests(user_id)
    list = []
    for request in requests:
        info = []
        info.append(getUsername(request))
        info.append(request)
        list.append(tuple(info))
    return list

def isFriend(user_id, friend_id):
    '''def isFriend(user_id, friend_id): check is user is friends with other user'''
    friends = getFriends(user_id)
    if friends is None:
        return False
    return (str(friend_id) in friends)

def isRequested(user_id, friend_id):
    '''def isRequested(user_id, friend_id): check if user has already requested friend'''
    requests = getRequests(friend_id)
    if requests is None:
        return False
    return (str(user_id) in requests)

def findUser(user_id, query):
    '''def findUser(query): search for a user'''
    query = query.lower().strip()
    list = []
    q = "SELECT username FROM user_tbl;"
    data = exec(q).fetchall()
    for name in data:
        info = []
        if (query in name[0].lower()):
            friend_id = getUserID(name[0])
            if (user_id != friend_id):
                info.append(name[0]) #name
                info.append(friend_id) #user_id
                friend = isFriend(user_id, friend_id)
                requested = isRequested(user_id, friend_id)
                print(requested)
                if friend: #color
                    info.append("btn-secondary")
                    info.append("disabled")
                    info.append("Added")
                else:
                    info.append("btn-primary")
                    if requested:
                        info.append("disabled")
                        info.append("Requested")
                    else:
                        info.append("")
                        info.append("Send Request")
                list.append(tuple(info))
    return list

def sendRequest(to_user, from_user):
    '''def sendRequest(to, from): send request to user from other user'''
    q = "SELECT requests FROM user_tbl WHERE user_id=?"
    inputs = (to_user, )
    requests = execmany(q, inputs).fetchone()[0]
    if requests is None:
        requests = str(from_user)
    else:
        requests += ',' + str(from_user)
    q = "UPDATE user_tbl SET requests=? WHERE user_id=?"
    inputs = (requests, to_user)
    execmany(q, inputs)

def processRequest(to_user, from_user, accepted):
    '''def acceptRequest(to, from): process request from other user'''
    #update to_user request list
    q = "SELECT requests FROM user_tbl WHERE user_id=?"
    inputs = (to_user, )
    requests = execmany(q, inputs).fetchone()[0]
    requests = requests.split(",")
    requests = requests.remove(str(from_user))
    if requests is not None:
        requests = requests.join(",")
    q = "UPDATE user_tbl SET requests=? WHERE user_id=?"
    inputs = (requests, to_user)
    execmany(q, inputs)

    if accepted:
        #update to_user friend list
        q = "SELECT friends FROM user_tbl WHERE user_id=?"
        inputs = (to_user, )
        friends = execmany(q, inputs).fetchone()[0]
        if friends is None:
            friends = str(from_user)
        else:
            friends += ',' + str(from_user)
        q = "UPDATE user_tbl SET friends=? WHERE user_id=?"
        inputs = (friends, to_user)
        execmany(q, inputs)

        #update from_user friend list
        q = "SELECT friends FROM user_tbl WHERE user_id=?"
        inputs = (from_user, )
        friends = execmany(q, inputs).fetchone()[0]
        if friends is None:
            friends = str(to_user)
        else:
            friends += ',' + str(to_user)
        q = "UPDATE user_tbl SET friends=? WHERE user_id=?"
        inputs = (friends, from_user)
        execmany(q, inputs)


#====================================================
# MANAGING JOURNAL ENTRIES

def updateEntry(username, entry):
    '''def updateEntry(username, entry): add a new entry to the journal_tbl'''
    idNum = getUserID(username)
    q = "SELECT entry_id FROM journal_tbl WHERE user_id=? AND date=?"
    today = datetime.now()
    date = today.date()
    inputs = (idNum, date)
    data = execmany(q, inputs).fetchone()
    print("updateEntry")
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
    print("getEntry")
    print(data)
    return data

def createTask(username, task, description, time, resolved):
    '''def createTask(username, date, text, time, resolved): create a to-do task for the current day'''
    idNum = getUserID(username)
    today = datetime.now()
    date = today.date()
    q = "INSERT INTO tdlist_tbl (user_id, date, task, description, time, resolved) VALUES(?, ?, ?, ?, ?, ?)"
    inputs = (idNum, date, task, description, time, resolved)
    execmany(q, inputs)

def getTasks(username, date):
    '''def getTasks(username, date): retrieve all tasks on the to-do list of a specified date'''
    idNum = getUserID(username)
    q = "SELECT entry_id FROM tdlist_tbl WHERE user_id=? AND date=?"
    inputs = (idNum, date)
    data = execmany(q, inputs).fetchall()
    print("getTask")
    # print(len(data))
    print(data)
    # print(data[1])
    list = []
    if(len(data) == 0):
        return ""
    else:
        for x in data:
            for y in x:
                q = "SELECT entry_id, task, description, time, resolved FROM tdlist_tbl WHERE user_id=? AND date=? AND entry_id=?"
                inputs = (idNum, date, y)
                temp = execmany(q, inputs).fetchone()
                list.append(temp)
        print(list)
        # print(list[0])
        # print(list[0][0])
        return list

def getSpecificTasks(username, date, resolved):
    '''def getSpecificTasks(username, date): retrieve tasks on the to-do list of a specified date based on their 'resolved' status'''
    idNum = getUserID(username)
    q = "SELECT entry_id FROM tdlist_tbl WHERE user_id=? AND date=? AND resolved=?"
    inputs = (idNum, date, resolved)
    data = execmany(q, inputs).fetchall()
    print("getSpecificTask")
    # print(len(data))
    print(data)
    # print(data[1])
    list = []
    if(len(data) == 0):
        return ""
    else:
        for x in data:
            for y in x:
                q = "SELECT entry_id, task, description, time, resolved FROM tdlist_tbl WHERE user_id=? AND date=? AND entry_id=?"
                inputs = (idNum, date, y)
                temp = execmany(q, inputs).fetchone()
                list.append(temp)
        print(list)
        # print(list[0])
        # print(list[0][0])
        return list

def removeTask(username, date, entryNum):
    '''def removeTask(username, date, entryNum): removes the task row from tdlist_tbl given the entry ID'''
    idNum = getUserID(username)
    q = "DELETE FROM tdlist_tbl WHERE entry_id=? AND user_id=? AND date=?"
    inputs = (entryNum, idNum, date)
    execmany(q, inputs)

def resolveTask(username, date, entryNum, resolve):
    '''def removeTask(username, date, entryNum): resolves the task row from tdlist_tbl given the entry ID'''
    idNum = getUserID(username)
    q = "UPDATE tdlist_tbl SET resolved=? WHERE entry_id=? AND user_id=? AND date=?"
    inputs = (resolve, entryNum, idNum, date)
    execmany(q, inputs)

def editTask(username, date, entryNum, task, description, time):
    '''def editTask(username, date, entryNum, task, description, time): edits task given changes'''
    idNum = getUserID(username)
    q = "UPDATE tdlist_tbl SET task=?, description=?, time=? WHERE entry_id=? AND user_id=? AND date=?"
    inputs = (task, description, time, entryNum, idNum, date)
    execmany(q, inputs)

#====================================================
# MANAGING TRACKERS

def addMood(user_id, date, mood):
    '''adds the mood into the mood table if it does not already exist,
       updates the mood if there is already a value inputed for the day'''
    if getMood(user_id, date) == ['None', '#ffffff']:
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
        return ['None', '#ffffff']
    else:
        return MOOD_DICT[data[0]]

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
