# standard library imports
from datetime import datetime
import random, sys
import sqlite3

# local application imports
from utl.db_builder import exec, execmany

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
        user_id = getUserID(username)
        q = "INSERT INTO future_tbl (user_id, type, title) VALUES(?, ?, ?)"
        inputs = (user_id, 0, "Bucket List")
        execmany(q, inputs)
        inputs = (user_id, 1, "Reading List")
        execmany(q, inputs)
        inputs = (user_id, 2, "To-Watch List")
        execmany(q, inputs)
        return True
    return False #if username already exists

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

def userExists(user_id):
    '''def userExists(user_id): return boolean to check if user exists'''
    q = "select username FROM user_tbl WHERE user_id=?"
    inputs = (user_id, )
    data = execmany(q, inputs).fetchone()
    return data is not None

#====================================================
# MANAGING FRIENDS

def getPermissions(user_id):
    '''def getPermissions(user_id): get user's permissions and convert into a dictionary'''
    q = "SELECT permissions FROM user_tbl WHERE user_id=?"
    inputs = (user_id,)
    data = execmany(q, inputs).fetchone()[0]
    dict = {0: [False, "View Mood Tracker"], 1: [False, "View Sleep Tracker"],
            2: [False, "View Monthly Calendars"], 3: [False, "View To-Do Lists"],
            4: [False, "Comment Access"], 5: [False, "View Future Spread"]}
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
                reverse_requested = isRequested(friend_id, user_id)
                if friend: #color
                    info.append("btn-secondary")
                    info.append("disabled")
                    info.append("Added")
                else:
                    info.append("btn-primary")
                    if requested:
                        info.append("disabled")
                        info.append("Requested")
                    elif reverse_requested:
                        info.append("")
                        info.append(None)
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
    requests.remove(str(from_user))
    requests = ",".join(requests)
    if (requests == ''):
        requests = None
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

def addComment(user_id, friend_id, date, comment):
    '''def addComment(user_id, friend_id, comment): add comment to a friend's journal entry'''
    q = "INSERT INTO comment_tbl(entry_id, commenter_id, comment) VALUES(?, ?, ?)"
    entry_id = getEntryId(friend_id, date)
    inputs = (entry_id, user_id, comment)
    execmany(q, inputs)

def getComments(user_id, entry_id):
    '''def getComments(user_id, entry_id): return list of comments on certain entry'''
    list = []
    q = "SELECT commenter_id, comment, comment_id FROM comment_tbl WHERE entry_id=?"
    inputs = (entry_id, )
    data = execmany(q, inputs).fetchall()
    if data is None:
        return []
    for comment in data:
        info = []
        info.append(getUsername(comment[0]))
        info.append(comment[1])
        list.append(tuple(info))
    return list

#====================================================
# MANAGING JOURNAL ENTRIES

def updateEntry(username, entry, date):
    '''def updateEntry(username, entry): add a new entry to the journal_tbl'''
    idNum = getUserID(username)
    q = "SELECT entry_id FROM journal_tbl WHERE user_id=? AND date=?"
    inputs = (idNum, date)
    data = execmany(q, inputs).fetchone()
    if(data is None):
        q = "INSERT INTO journal_tbl (user_id, date, body) VALUES(?, ?, ?)"
        inputs = (idNum, date, entry)
        execmany(q, inputs)
    else:
        q = "UPDATE journal_tbl SET body=? WHERE user_id=? AND date=?"
        inputs = (entry, idNum, date)
        execmany(q, inputs)

def getEntry(user, date):
    '''def getEntry(username, date): retrieve the body text of the user at the specified date'''
    # idNum = getUserID(username)
    q = "SELECT body FROM journal_tbl WHERE user_id=? AND date=?"
    inputs = (user, date)
    data = execmany(q, inputs).fetchone()
    return data

def getEntryId(user, date):
    '''def getEntryId(user, date): get entry_id for entry made by user on certain date'''
    q = "SELECT entry_id FROM journal_tbl WHERE user_id=? AND date=?"
    inputs = (user, date)
    data = execmany(q, inputs).fetchone()
    if data is None: #no entry found
        return -1
    return data[0]

def createTask(username, task, description, time, resolved, date):
    '''def createTask(username, date, text, time, resolved): create a to-do task for the current day'''
    idNum = getUserID(username)
    q = "INSERT INTO tdlist_tbl (user_id, date, task, description, time, resolved) VALUES(?, ?, ?, ?, ?, ?)"
    inputs = (idNum, date, task, description, time, resolved)
    execmany(q, inputs)

def getTasks(user, date):
    '''def getTasks(username, date): retrieve all tasks on the to-do list of a specified date'''
    # idNum = getUserID(username)
    q = "SELECT entry_id FROM tdlist_tbl WHERE user_id=? AND date=?"
    inputs = (user, date)
    data = execmany(q, inputs).fetchall()
    # print(len(data))
    # print(data[1])
    list = []
    if(len(data) == 0):
        return ""
    else:
        for x in data:
            for y in x:
                q = "SELECT entry_id, task, description, time, resolved FROM tdlist_tbl WHERE user_id=? AND date=? AND entry_id=?"
                inputs = (user, date, y)
                temp = execmany(q, inputs).fetchone()
                list.append(temp)
        # print(list[0])
        # print(list[0][0])
        return list

def getSpecificTasks(user, date, resolved):
    '''def getSpecificTasks(username, date): retrieve tasks on the to-do list of a specified date based on their 'resolved' status'''
    # idNum = getUserID(username)
    q = "SELECT entry_id FROM tdlist_tbl WHERE user_id=? AND date=? AND resolved=?"
    inputs = (user, date, resolved)
    data = execmany(q, inputs).fetchall()
    # print(len(data))
    # print(data[1])
    list = []
    if(len(data) == 0):
        return ""
    else:
        for x in data:
            for y in x:
                q = "SELECT entry_id, task, description, time, resolved FROM tdlist_tbl WHERE user_id=? AND date=? AND entry_id=?"
                inputs = (user, date, y)
                temp = execmany(q, inputs).fetchone()
                list.append(temp)
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
    '''def resolveTask(username, date, entryNum): resolves the task row from tdlist_tbl given the entry ID'''
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

def addSleep(user_id, date, sleep):
    '''adds the sleep into the sleep table if it does not already exist,
       updates the sleep if there is already a value inputed for the day'''
    if getSleep(user_id, date) == None:
        q = "INSERT INTO sleep_tbl VALUES(?, ?, ?)"
        inputs = (user_id, date, sleep)
        execmany(q, inputs)
    else:
        q = "UPDATE sleep_tbl SET sleep = ? WHERE user_id = ? AND date = ?"
        inputs = (sleep, user_id, date)
        execmany(q, inputs)

def getSleep(user_id, date):
    '''returns the hours of sleep for the given date and user
       returns None if user did not input data for the day'''
    q = "SELECT sleep FROM sleep_tbl WHERE user_id = ? AND date = ?"
    inputs = (user_id, date,)
    data = execmany(q, inputs).fetchone()
    if data is None:
        return None
    else:
        return data[0]

def getMonthSleep(user_id, month_year):
    '''returns a list of all the hours of sleep in the given month for the given user in the format:
        [{'date': <date>, 'sleep': <sleep>}, ... ]
    '''
    q = "SELECT date, sleep FROM sleep_tbl WHERE user_id = ? AND date LIKE ?"
    inputs = (user_id, month_year + '%',)
    data = execmany(q, inputs)
    dict = []
    for row in data:
        dict.append({'date': row[0], 'sleep': row[1]})
    return dict

#====================================================
# MANAGING FUTURE LISTS

def addList(user_id, title, collaborators):
    '''def addList(user_id, title, collaborators): adds list by user with given title and collaborators'''
    q = "INSERT INTO future_tbl (user_id, type, title, collaborators) VALUES(?, ?, ?, ?)"
    temp = collaborators #store list of collaborators
    collaborators = ",".join(collaborators)
    if collaborators == "":
        collaborators = None
    inputs = (user_id, 3, title, collaborators)
    list_id = execmany(q, inputs).lastrowid
    for collaborator in temp:
        sendMessage(user_id, collaborator, list_id)

def sendMessage(user_id, friend_id, list_id):
    '''def sendMessage(user_id, friend_id, list_id): send message to a friend from user'''
    q = "SELECT newlists FROM user_tbl WHERE user_id=?"
    inputs = (friend_id, )
    newlists = execmany(q, inputs).fetchone()[0]
    if newlists is None:
        newlists = []
    else:
        newlists = newlists.split(",")
    entry = str(user_id) + "/" + str(list_id)
    newlists.append(entry)
    newlists = ",".join(newlists)
    q = "UPDATE user_tbl SET newlists=? WHERE user_id=?"
    inputs = (newlists, friend_id)
    execmany(q, inputs)

def getMessages(user_id):
    '''def getMessages(user_id): get user's messages'''
    q = "SELECT newlists FROM user_tbl WHERE user_id=?"
    inputs = (user_id, )
    newlists = execmany(q, inputs).fetchone()[0]
    if newlists is None:
        return []
    return newlists.split(",")

def formatMessages(user_id):
    '''def formatMessages(user_id): format output of getMessages()'''
    messages = getMessages(user_id)
    list = []
    if len(messages) == 0:
        return []
    for message in messages:
        info = []
        message = message.split("/")
        user_id = int(message[0])
        username = getUsername(user_id)
        list_id = int(message[1])
        list_title = getTitle(list_id)
        info.append(user_id)
        info.append(username)
        info.append(list_id)
        info.append(list_title)
        list.append(tuple(info))
    return list

def removeMessage(friend_id, user_id, list_id):
    '''def removeMessage(friend_id, user_id, list_id): remove friend's message with specified list_id from user's messages'''
    q = "SELECT newlists FROM user_tbl WHERE user_id=?"
    inputs = (user_id, )
    newlists = execmany(q, inputs).fetchone()[0]
    if newlists is None:
        newlists = []
    else:
        newlists = newlists.split(",")
    entry = str(friend_id) + "/" + str(list_id)
    try:
        newlists.remove(entry)
    except ValueError:
        pass
    if len(newlists) == 0:
        newlists = None
    else:
        newlists = ",".join(newlists)
    q = "UPDATE user_tbl SET newlists=? WHERE user_id=?"
    inputs = (newlists, user_id)
    execmany(q, inputs)

def addItem(list_id, item):
    '''def addItem(list_id, item): add item to given list'''
    q = "INSERT INTO listitem_tbl (item, resolved) VALUES(?, ?)"
    inputs = (item, 0)
    item_id = execmany(q, inputs).lastrowid
    q = "SELECT items FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    items = execmany(q, inputs).fetchone()
    if items is not None:
        items = items[0]
        if items is None:
            items = []
        else:
            items = items.split(",")
    else:
        items = []
    items.append(str(item_id))
    items = ",".join(items)
    q = "UPDATE future_tbl SET items=? WHERE list_id=?"
    inputs = (items, list_id)
    execmany(q, inputs)

def deleteItem(list_id, item_id):
    '''def deleteItem(list_id, item_id): remove item from list'''
    q = "DELETE from listitem_tbl WHERE item_id=?"
    inputs = (item_id, )
    execmany(q, inputs)
    q = "SELECT items FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    items = execmany(q, inputs).fetchone()[0]
    items = items.split(",")
    items.remove(str(item_id))
    items = ",".join(items)
    if items == "":
        items = None
    q = "UPDATE future_tbl SET items=? WHERE list_id=?"
    inputs = (items, list_id)
    execmany(q, inputs)

def resolveItem(item_id):
    '''def resolveItem(item_id): resolve a specific item'''
    q = "SELECT resolved FROM listitem_tbl WHERE item_id=?"
    inputs = (item_id, )
    resolved = execmany(q, inputs).fetchone()[0]
    if resolved == 0:
        resolved = 1
    else:
        resolved = 0
    q = "UPDATE listitem_tbl SET resolved=? WHERE item_id=?"
    inputs = (resolved, item_id)
    execmany(q, inputs)

def editItem(item_id, item):
    '''def editItem(item_id, item): edit specific item'''
    q = "UPDATE listitem_tbl SET item=? WHERE item_id=?"
    inputs = (item, item_id)
    execmany(q, inputs)

def getItemsFromList(list_id):
    '''def getItemsFromList(list_id): return all items in a list with resolved status'''
    q = "SELECT items FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    items = execmany(q, inputs).fetchone()
    if items is not None:
        items = items[0]
        if items is None:
            return []
        items = items.split(",")
        list = []
        for item in items:
            info = []
            item_id = int(item)
            info.append(item_id)
            q = "SELECT item FROM listitem_tbl WHERE item_id=?"
            inputs = (item_id, )
            item = execmany(q, inputs).fetchone()[0]
            info.append(item)
            q = "SELECT resolved FROM listitem_tbl WHERE item_id=?"
            resolved = int(execmany(q, inputs).fetchone()[0]) == 1
            info.append(resolved)
            list.append(tuple(info))
        return list
    else:
        return []

def deleteList(list_id):
    '''def deleteList(list_id): delete specified list'''
    q = "SELECT type FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    type = execmany(q, inputs).fetchone()[0]
    if type == 3:
        q = "SELECT items from future_tbl WHERE list_id=?"
        items = execmany(q, inputs).fetchone()
        if items is not None:
            items = items[0]
            if items is not None:
                items = items.split(",")
                for item in items:
                    item_id = int(item)
                    deleteItem(list_id, item_id)
        q = "DELETE from future_tbl WHERE list_id=?"
        execmany(q, inputs)
        return True
    return False #cannot delete default lists

def editTitle(list_id, title):
    '''def editTitle(list_id, title): edit title for given list'''
    q = "UPDATE future_tbl SET title=? WHERE list_id=?"
    inputs = (title, list_id)
    execmany(q, inputs)

def addCollaborators(list_id, collaborators):
    '''def addCollaborators(list_id, collaborators): add collaborators to list'''
    q = "SELECT type FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    type = execmany(q, inputs).fetchone()[0]
    if type == 3:
        q = "SELECT collaborators FROM future_tbl WHERE list_id=?"
        data = execmany(q, inputs).fetchone()
        if data is not None:
            data = data[0]
            data += "," + ",".join(collaborators)
        else:
            data = ",".join(collaborators)
        q = "UPDATE future_tbl SET collaborators=? WHERE list_id=?"
        inputs = (data, list_id)
        execmany(q, inputs)
        return True
    return False

def getTitle(list_id):
    '''def getTitle(list_id): get title of specified list'''
    q = "SELECT title FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    data = execmany(q, inputs).fetchone()[0]
    return data

def getCollaborators(list_id):
    '''def getCollaborators(list_id): return list of collaborators with their usernames'''
    q = "SELECT collaborators FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    data = execmany(q, inputs).fetchone()
    if data is None:
        return []
    data = data[0]
    if data is None:
        return []
    data = data.split(",")
    list = []
    for collaborator in data:
        info = []
        info.append(int(collaborator))
        info.append(getUsername(int(collaborator)))
        list.append(tuple(info))
    return list

def getCollaboratorId(list_id):
    '''def getCollaboratorId(list_id): get IDs of collaborators'''
    q = "SELECT collaborators FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    data = execmany(q, inputs).fetchone()
    if data is None:
        return []
    data = data[0]
    if data is None:
        return []
    data = data.split(",")
    list = []
    for collaborator in data:
        list.append(collaborator)
    return list

def updateCollaborators(list_id, collaborators):
    '''def updateCollaborators(list_id, collaborators): update collaborators on specified list'''
    friend_id = getOwner(list_id)[0]
    old_collaborators = getCollaboratorId(list_id)
    for person in old_collaborators:
        user_id = int(person)
        removeMessage(friend_id, user_id, list_id)
    for person in collaborators:
        to_id = person
        sendMessage(friend_id, to_id, list_id)
    collaborators = ",".join(collaborators)
    if collaborators == "":
        collaborators = None
    q = "UPDATE future_tbl SET collaborators=? WHERE list_id=?"
    inputs = (collaborators, list_id)
    execmany(q, inputs)

def canEdit(list_id, user_id):
    '''def canEdit(list_id, user_id): returns whether or not user is allowed to edit list'''
    q = "SELECT user_id FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    data = execmany(q, inputs).fetchone()[0]
    if str(user_id) == str(data):
        return True
    q = "SELECT collaborators FROM future_tbl WHERE list_id=?"
    data = execmany(q, inputs).fetchone()
    if data is None:
        return False
    data = data[0]
    if data is None:
        return False
    data = data.split(",")
    return (str(user_id) in data)

def getOwner(list_id):
    '''def getOwner(list_id): get owner of specified list'''
    q = "SELECT user_id FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    user_id = execmany(q, inputs).fetchone()[0]
    info = []
    info.append(user_id)
    info.append(getUsername(user_id))
    return tuple(info)

def getType(list_id):
    '''def getType(list_id): get type of specified list'''
    q = "SELECT type FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    type = execmany(q, inputs).fetchone()[0]
    return type

def getLists(user_id):
    '''def getLists(user_id): returns array of list_ids that user can edit'''
    q = "SELECT list_id FROM future_tbl"
    data = exec(q)
    list = []
    for id in data:
        list_id = id[0]
        if canEdit(list_id, user_id):
            info = []
            info.append(list_id)
            info.append(getTitle(list_id))
            info.append(getItemsFromList(list_id))
            info.append(getOwner(list_id))
            info.append(getCollaborators(list_id))
            info.append(getType(list_id))
            list.append(info)
    return list

def listExists(list_id):
    '''def listExists(list_id): check to see if list exists'''
    q = "SELECT list_id FROM future_tbl WHERE list_id=?"
    inputs = (list_id, )
    data = execmany(q, inputs).fetchone()
    return data is not None
