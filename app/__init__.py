#Team Ducking Awesome
#SoftDev pd1
#P05 -- Fin
#2020-06-11

# standard library imports
from datetime import datetime
from functools import wraps
import sqlite3, os, random

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
    if ("," in username):
            flash('Commas are not allowed in username!', 'alert-danger')
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
    if not db_manager.userExists(user):
        return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))
    today = datetime.now()
    now = "" + today.strftime("%A") + ", " + today.strftime("%B") + " " + today.strftime("%d") + ", " + today.strftime("%Y")
    session['date'] = now
    entry_id = db_manager.getEntryId(user, today.date())
    text = db_manager.getEntry(user, today.date())
    unresolved = db_manager.getSpecificTasks(user, today.date(), 0)
    resolved = db_manager.getSpecificTasks(user, today.date(), 1)
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

    if(text is None):
        hide = "no"
    else:
        hide = "yes"
    # print(user)
    # print(date)
    mood_vals = db_manager.getMood(user, date)
    # print(mood_vals)
    sleep_vals = db_manager.getSleep(user, date)
    if (int(user) == session['user_id']):
        isOwner = True
    else:
        isOwner = False
    viewmood = permissions.get(0)[0]
    viewsleep = permissions.get(1)[0]
    viewperiod = permissions.get(2)[0]
    viewtd = permissions.get(3)[0]
    comment = permissions.get(4)[0]
    viewentry = db_manager.isFriend(session['user_id'], int(user))
    if isOwner:
        comment = True
        viewtd = True
        viewsleep = True
        viewmood = True
        viewperiod = True
        viewentry = True
    return render_template("daily.html", isLogin=False, daily="active", date = session['date'], entries = text, isOwner=isOwner, datetime=date, hide = hide, mood=mood_vals, tasks = tasks, sleep=sleep_vals,
                                         comments=comments, user_id=user, entry_id=entry_id, entrydate=today, comment=comment, viewmood=viewmood, viewsleep=viewsleep, viewperiod=viewperiod, viewtd=viewtd, viewentry=viewentry)


@app.route("/entrycheck", methods=["GET", "POST"])
@login_required
def entry():
    entry = request.form['new_entry']
    db_manager.updateEntry(session['username'], entry)
    return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))

@app.route("/editentry", methods=["GET", "POST"])
@login_required
def edit():
    entry = request.form['edit_entry']
    db_manager.updateEntry(session['username'], entry)
    return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))

@app.route("/taskcheck", methods=["GET", "POST"])
@login_required
def task():
    task = request.form['task']
    description = request.form['description']
    time = request.form['time']
    print(task)
    print(description)
    print(time)
    if (task == "" and description == "" and time == ""):
        return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))
    db_manager.createTask(session['username'], task, description, time, 0)
    return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))

@app.route("/edittask", methods=["GET", "POST"])
@login_required
def taskedit():
    today = datetime.now()
    tasks = db_manager.getTasks(session['user_id'], today.date())

    toRemove = ""
    toResolve = ""
    toUnresolve = ""

    toChange = ""
    changeTask = ""
    changeDescription = ""
    changeTime = ""

    print("==================")
    for x in tasks:
        entryID = str(x[0])
        delete = 'delete_task' + entryID
        print(delete)
        resolve = 'resolve_task' + entryID
        unresolve = 'unresolve_task' + entryID
        taskEdit = 'task' + entryID
        descriptionEdit = 'description' + entryID
        timeEdit = 'time' + entryID
        if(delete in request.form):
            print("yes delete")
            toRemove = request.form[delete]
            print(toRemove)
            break
        elif(resolve in request.form):
                print("yes resolve")
                toResolve = request.form[resolve]
                print(toResolve)
                break
        elif(unresolve in request.form):
                print("yes unresolve")
                toUnresolve = request.form[unresolve]
                print(toUnresolve)
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
        db_manager.removeTask(session['username'], today.date(), int(toRemove))
    if(toResolve != ""):
        db_manager.resolveTask(session['username'], today.date(), int(toResolve), 1)
    if(toUnresolve != ""):
        db_manager.resolveTask(session['username'], today.date(), int(toUnresolve), 0)

    print("change")
    print(changeTask)
    print(changeDescription)
    print(changeTime)

    if(toChange != ""):
        db_manager.editTask(session['username'], today.date(), int(toChange), changeTask, changeDescription, changeTime)

    return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))

@app.route("/moodcheck", methods=["GET","POST"])
@login_required
def mood():
    db_manager.addMood(session['user_id'], request.form['date'], request.form['mood'])
    return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))

@app.route("/sleepcheck", methods=["GET","POST"])
@login_required
def sleep():
    db_manager.addSleep(session['user_id'], request.form['date'], request.form['sleep'])
    return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))

@app.route("/addcomment", methods=["POST"])
@login_required
def addcomment():
    user_id = session['user_id']
    friend_id = request.form['user_id']
    comment = request.form['commentbody']
    date = datetime.date(datetime.now())
    if comment != '':
        db_manager.addComment(user_id, friend_id, date, comment)
    return redirect(url_for("daily", user=friend_id, date=date))

@app.route("/monthly", methods=["GET", "POST"])
@login_required
def monthly():
    if 'month' in request.form:
        date = MONTHS[request.form['month']] + ' ' + request.form['year']
        moods = db_manager.getMonthMoods(session['user_id'], request.form['year'] + '-' + request.form['month'])
    else:
        date = datetime.now().strftime('%B') + ' ' + str(datetime.now().year)
        moods = db_manager.getMonthMoods(session['user_id'], str(datetime.now().year) + '-' + datetime.now().strftime('%m'))
    return render_template("monthly.html", isLogin=False, monthly="active", date=date, moods=moods)

@app.route("/friends")
@login_required
def friends():
    user_id = session['user_id']
    permissions = db_manager.getPermissions(user_id)
    friendlist = db_manager.formatFriends(user_id)
    requests = db_manager.formatRequests(user_id)
    date = datetime.now().date()
    return render_template("friends.html", isLogin=False, friends="active", edit=False, permissions=permissions.items(), friendlist=friendlist, requests=requests, date=date)

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
    return render_template("friends.html", isLogin=False, friends="active", edit=True, permissions=permissions.items(), friendlist=friendlist, requests=requests, date=date)

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
    return render_template("addfriends.html", isLogin=False, addfriends="active", users=users, search=search, query=query)

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
