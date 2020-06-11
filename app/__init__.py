#Team Ducking Awesome
#SoftDev pd1
#P05 -- Fin
#2020-06-11

# standard library imports
from datetime import datetime
from functools import wraps
import sqlite3, os, random
import math

# third-party imports
from flask import Flask, render_template, request, redirect, url_for, session, flash

# local application imports
from utl import db_builder, db_manager


app = Flask(__name__)
app.secret_key = os.urandom(32)
MONTHS = {'01': 'January', '02': 'February', '03': 'March', '04': 'April',
          '05': 'May', '06': 'June', '07': 'July', '08': 'August',
          '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

#====================================================
# FUNCTION WRAPPERS FOR LOGIN

def login_required(f):
    '''Decorator for making sure user is logged in'''
    @wraps(f)
    def dec(*args, **kwargs):
        '''dec (*args, **kwargs): Decorator for checking login and if user in session'''
        if 'username' in session:
            for arg in args:
                print(arg)
            return f(*args, **kwargs)
        flash('You must be logged in to view this page!', 'alert-danger')
        return redirect('/')
    return dec

def no_login_required(f):
    '''Decorator for making sure user is not logged in'''
    @wraps(f)
    def dec(*args, **kwargs):
        '''dec(*args, **kwargs): Decorator for checking no login'''
        if 'username' not in session:
            return f(*args, **kwargs)
        flash('You cannot view this page while logged in!', 'alert-danger')
        return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))
    return dec

#====================================================
# LOGIN FUNCTIONS

@app.route("/")
def root():
    '''def root(): Redirects to login page if not in session, redirects to daily if in session'''
    if 'username' in session: #if logged in
        return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))
    return redirect('/login')

@app.route("/login")
@no_login_required
def login():
    '''def login(): login requirement'''
    return render_template('login.html', isLogin=True, login="active")

@app.route("/auth", methods=["POST"])
@no_login_required
def auth():
    '''def auth(): authenticating login and flashing corresponding errors'''
    enteredU = request.form['username']
    enteredP = request.form['password']
    if(enteredU == "" or enteredP == ""): #if fields empty
        flash('Please fill out all fields!', 'alert-danger')
        return redirect(url_for('login'))
    if (db_manager.userValid(enteredU, enteredP)): #returns true if login successful
        flash('Welcome back, ' + enteredU + "!", 'alert-success')
        session['username'] = enteredU
        session['user_id'] = db_manager.getUserID(enteredU)
        return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))
    else:
        flash('Wrong Credentials!', 'alert-danger')
        return redirect(url_for('login'))

@app.route("/signup")
@no_login_required
def signup():
    '''def signup(): sign up route, takes in a form for signing up'''
    return render_template("signup.html", isLogin=True, signup="active")

@app.route("/signupcheck", methods=["POST"])
@no_login_required
def signupcheck():
    '''def signupcheck(): Checking if sign up form is filled out correctly; i.e. username taken, passwords match, all fields filled out'''
    username = request.form['username']
    password = request.form['password']
    confirm = request.form['confirmation']
    #preliminary checks on entered fields
    if(username == "" or password == "" or confirm == ""):
        flash('Please fill out all fields!', 'alert-danger')
        return render_template("signup.html", username=username, password=password, confirm=confirm, isLogin=True, signup="active")
    if (confirm!=password):
        flash('Passwords do not match!', 'alert-danger')
        return render_template("signup.html", username=username, password=password, confirm=confirm, isLogin=True, signup="active")
    #form information delivered to backend
    added = db_manager.addUser(username,password) #returns True if user was sucessfully added
    if (not added):
        flash('Username taken!', 'alert-danger')
        return render_template("signup.html", username=username, password=password, confirm=confirm, isLogin=True, signup="active")
    flash('You have successfully created an account! Please log in!', 'alert-success')
    return redirect(url_for('login'))

#====================================================
# STARTING HERE, USER MUST BE LOGGED IN

@app.route("/daily/<user>/<date>")
@login_required
def daily(user,date):
    if not db_manager.userExists(user): #if faulty url, redirect to default entry for today
        return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))
    username = db_manager.getUsername(user)
    date = datetime.strptime(date, "%Y-%m-%d").date()
    fulldate = "" + date.strftime("%A") + ", " + date.strftime("%B") + " " + date.strftime("%d") + ", " + date.strftime("%Y")
    entry_id = db_manager.getEntryId(user, date)
    text = db_manager.getEntry(user, date)
    unresolved = db_manager.getSpecificTasks(user, date, 0)
    resolved = db_manager.getSpecificTasks(user, date, 1)
    comments = db_manager.getComments(user, entry_id)
    permissions = db_manager.getPermissions(user)
    if(unresolved == "" and resolved == ""):
        tasks = ""
    elif(unresolved == ""):
        tasks = resolved
    elif(resolved == ""):
        tasks = unresolved
    else:
        tasks = unresolved + resolved
    mood_vals = db_manager.getMood(user, date)
    sleep_vals = db_manager.getSleep(user, date)
    if (int(user) == session['user_id']):
        isOwner = True
    else:
        isOwner = False
    comment = False
    viewtd = False
    viewsleep = False
    viewmood = False
    viewentry = False
    isFriend = db_manager.isFriend(session['user_id'], int(user))
    if isOwner:
        comment = True
        viewtd = True
        viewsleep = True
        viewmood = True
        viewentry = True
    elif isFriend:
        viewmood = permissions.get(0)[0]
        viewsleep = permissions.get(1)[0]
        viewtd = permissions.get(3)[0]
        comment = permissions.get(4)[0]
        viewentry = True
    return render_template("daily.html", isLogin=False, daily="active", date=fulldate, entries=text, isOwner=isOwner, datetime=date, mood=mood_vals, tasks=tasks, sleep=sleep_vals, username=username, default_id=session['user_id'],
                                         comments=comments, user_id=user, entry_id=entry_id, comment=comment, viewmood=viewmood, viewsleep=viewsleep, viewtd=viewtd, viewentry=viewentry, currentuser=session['username'])

@app.route("/changedate", methods=["POST"])
@login_required
def changedate():
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    user = request.form['user_id']
    return redirect(url_for('daily', user=user, date=date))

@app.route("/entrycheck", methods=["POST"])
@login_required
def entry():
    entry = request.form['new_entry']
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    db_manager.updateEntry(session['username'], entry, date)
    return redirect(url_for('daily', date=date, user=session['user_id']))

@app.route("/editentry", methods=["POST"])
@login_required
def edit():
    entry = request.form['edit_entry']
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    db_manager.updateEntry(session['username'], entry, date)
    return redirect(url_for('daily', date=date, user=session['user_id']))

@app.route("/taskcheck", methods=["POST"])
@login_required
def task():
    task = request.form['task']
    description = request.form['description']
    time = request.form['time']
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    if (task == "" and description == "" and time == ""):
        return redirect(url_for('daily', date=date, user=session['user_id']))
    db_manager.createTask(session['username'], task, description, time, 0, date)
    return redirect(url_for('daily', date=date, user=session['user_id']))

@app.route("/edittask", methods=["POST"])
@login_required
def taskedit():
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    tasks = db_manager.getTasks(session['user_id'], date)

    toRemove = ""
    toResolve = ""
    toUnresolve = ""

    toChange = ""
    changeTask = ""
    changeDescription = ""
    changeTime = ""

    for x in tasks:
        entryID = str(x[0])
        delete = 'delete_task' + entryID
        resolve = 'resolve_task' + entryID
        unresolve = 'unresolve_task' + entryID
        taskEdit = 'task' + entryID
        descriptionEdit = 'description' + entryID
        timeEdit = 'time' + entryID
        if(delete in request.form):
            toRemove = request.form[delete]
            break
        elif(resolve in request.form):
                toResolve = request.form[resolve]
                break
        elif(unresolve in request.form):
                toUnresolve = request.form[unresolve]
                break
        else:
            if(taskEdit in request.form):
                toChange = entryID
                changeTask = request.form[taskEdit]
            if(descriptionEdit in request.form):
                toChange = entryID
                changeDescription = request.form[descriptionEdit]
            if(timeEdit in request.form):
                toChange = entryID
                changeTime = request.form[timeEdit]
                break
    if(toRemove != ""):
        db_manager.removeTask(session['username'], date, int(toRemove))
    if(toResolve != ""):
        db_manager.resolveTask(session['username'], date, int(toResolve), 1)
    if(toUnresolve != ""):
        db_manager.resolveTask(session['username'], date, int(toUnresolve), 0)

    if(toChange != ""):
        db_manager.editTask(session['username'], date, int(toChange), changeTask, changeDescription, changeTime)

    return redirect(url_for('daily', date=date, user=session['user_id']))

@app.route("/moodcheck", methods=["POST"])
@login_required
def mood():
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    db_manager.addMood(session['user_id'], date, request.form['mood'])
    return redirect(url_for('daily', date=date, user=session['user_id']))

@app.route("/sleepcheck", methods=["POST"])
@login_required
def sleep():
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    db_manager.addSleep(session['user_id'], date, request.form['sleep'])
    return redirect(url_for('daily', date=date, user=session['user_id']))

@app.route("/addcomment", methods=["POST"])
@login_required
def addcomment():
    user_id = session['user_id']
    friend_id = request.form['user_id']
    comment = request.form['commentbody']
    date = request.form['date']
    date = datetime.strptime(date, "%Y-%m-%d").date()
    if comment != '':
        db_manager.addComment(user_id, friend_id, date, comment)
    return redirect(url_for("daily", user=friend_id, date=date))

#====================================================
# MONTHLY SPREAD

@app.route("/monthly/<user>", methods=["GET", "POST"])
@login_required
def monthly(user):
    username = db_manager.getUsername(user)
    isOwner = (str(session['user_id']) == user)
    permissions = db_manager.getPermissions(user)
    viewcal = False
    if isOwner:
        viewcal = True
    elif (db_manager.isFriend(session['user_id'], int(user))):
        viewcal = permissions.get(2)[0]
    if 'month' in request.form:
        month = request.form['month']
        year = request.form['year']
        date = MONTHS[month] + ' ' + year
        moods = db_manager.getMonthMoods(user, request.form['year'] + '-' + request.form['month'])
        sleeps = db_manager.getMonthSleep(user, request.form['year'] + '-' + request.form['month'])
    else:
        year = datetime.now().strftime('%Y')
        date = datetime.now().strftime('%B') + ' ' + year
        month = datetime.now().strftime('%m')
        moods = db_manager.getMonthMoods(user, str(datetime.now().year) + '-' + datetime.now().strftime('%m'))
        sleeps = db_manager.getMonthSleep(user, str(datetime.now().year) + '-' + datetime.now().strftime('%m'))
    return render_template("monthly.html", default_id=session['user_id'], username=username, isOwner=isOwner, isLogin=False, monthly="active",
                            date=date, month=month, year=year, moods=moods, sleeps=sleeps, currentuser=session['username'], viewcal=viewcal, user=user)

#====================================================
# FRIENDS

@app.route("/friends")
@login_required
def friends():
    user_id = session['user_id']
    permissions = db_manager.getPermissions(user_id)
    friendlist = db_manager.formatFriends(user_id)
    requests = db_manager.formatRequests(user_id)
    date = datetime.now().date()
    return render_template("friends.html", default_id=session['user_id'], isLogin=False, friends="active", edit=False, permissions=permissions.items(), friendlist=friendlist, requests=requests, date=date, currentuser=session['username'])

@app.route("/processrequest", methods=["POST"])
@login_required
def processrequest():
    user_id = session['user_id']
    value = request.form['response']
    friend_id = request.form['id']
    if value == '0':
        db_manager.processRequest(user_id, friend_id, False)
    else:
        db_manager.processRequest(user_id, friend_id, True)
    return redirect(url_for("friends"))

@app.route("/permissions")
@login_required
def permissions():
    user_id = session['user_id']
    permissions = db_manager.getPermissions(user_id)
    friendlist = db_manager.formatFriends(user_id)
    requests = db_manager.formatRequests(user_id)
    date = datetime.now().date()
    return render_template("friends.html", default_id=session['user_id'], isLogin=False, friends="active", edit=True, permissions=permissions.items(), friendlist=friendlist, requests=requests, date=date, currentuser=session['username'])

@app.route("/editpermissions", methods=["POST"])
@login_required
def editpermissions():
    user_id = session['user_id']
    permissions = 0
    options = request.form.getlist("options")
    for entry in options:
        permissions += pow(10, int(entry))
    db_manager.updatePermissions(user_id, permissions)
    return redirect(url_for("friends"))

@app.route("/addfriends", methods=["GET", "POST"])
@login_required
def addfriends():
    user_id = session['user_id']
    users = []
    search = False
    query = ''
    if request.method == "GET":
        if request.args:
            if ('query' in request.args):
                query = request.args['query']
                users = db_manager.findUser(user_id, query)
                search = True
    else:
        id = request.form['id']
        db_manager.sendRequest(id, user_id)
        query = request.form['query']
        return redirect(url_for("addfriends", query=query))
    return render_template("addfriends.html", default_id=session['user_id'], isLogin=False, addfriends="active", users=users, search=search, query=query, currentuser=session['username'])

#====================================================
# FUTURE SPREAD

@app.route("/future/<user>")
@login_required
def future(user):
    lists = db_manager.getLists(user)
    length = math.ceil(len(lists) / 3)
    isOwner = session['user_id'] == int(user)
    friendlist = db_manager.formatFriends(int(user))
    return render_template("future.html", default_id=session['user_id'], isLogin=False, future="active", currentuser=session['username'], lists=lists, length=length, isOwner=isOwner, friendlist=friendlist)

@app.route("/addnewlist", methods=["POST"])
@login_required
def addnewlist():
    user_id = request.form['user']
    title = request.form['title']
    options = request.form.getlist("options")
    db_manager.addList(user_id, title, options)
    return redirect(url_for("future", user=user_id))

@app.route("/editlist/<list>", methods=["GET", "POST"])
@login_required
def editlist(list):
    if request.method == "GET":
        exists = db_manager.listExists(list)
        if not exists:
            flash("You do not have access to that list!", 'alert-danger')
            return redirect(url_for('future', user=session['user_id']))
        canEdit = db_manager.canEdit(list, session['user_id'])
        if not canEdit:
            flash("You do not have access to that list!", 'alert-danger')
            return redirect(url_for('future', user=session['user_id']))
        title = db_manager.getTitle(list)
        items = db_manager.getItemsFromList(list)
        owner = db_manager.getOwner(list)
        collaborators = db_manager.getCollaborators(list)
        type = db_manager.getType(list)
        return render_template("list.html", default_id=session['user_id'], isLogin=False, future="active", currentuser=session['username'],
                                title=title, items=items, owner=owner, collaborators=collaborators, type=type, list=list)
    else:
        list_id = request.form['list']
        item = request.form['item']
        db_manager.addItem(list_id, item)
        return redirect(url_for('editlist', list=list, code=303))

#====================================================
# LOGOUT AND MAIN

@app.route("/logout")
@login_required
def logout():
    '''def logout(): logging out of session, redirects to login page'''
    session.clear()
    flash('You were successfully logged out.', 'alert-success')
    return redirect('/')

if __name__ == "__main__":
    db_builder.build_db()
    app.debug = True
    app.run()
