#Team Ducking Awesome
#SoftDev pd1
#P05 -- Fin
#2020-06-11

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3, os, random
from utl import db_builder, db_manager
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)

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
        flash('You were successfully logged in!', 'alert-success')
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
    today = datetime.now()
    now = "" + today.strftime("%A") + ", " + today.strftime("%B") + " " + today.strftime("%d") + ", " + today.strftime("%Y")
    session['date'] = now
    text = db_manager.getEntry(session['username'], today.date())
    if(text is None):
        hide = "no"
    else:
        hide = "yes"
    if (int(user) == session['user_id']):
        isOwner = True
    else:
        isOwner = False
    return render_template("daily.html", isLogin=False, daily="active", date = session['date'], entries = text, isOwner=isOwner, datetime=date, hide = hide)


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

@app.route("/moodcheck", methods=["GET","POST"])
@login_required
def mood():
    moods = request.form['mood']
    print(moods)
    date = request.form['date']
    print(date)
    return redirect(url_for('daily', date=datetime.date(datetime.now()), user=session['user_id']))

@app.route("/monthly")
@login_required
def monthly():
    return render_template("monthly.html", isLogin=False, monthly="active")

@app.route("/friends")
@login_required
def friends():
    username = session['username']
    permissions = db_manager.getPermissions(username)
    return render_template("friends.html", isLogin=False, friends="active", edit=False, permissions=permissions.items())

@app.route("/friends")
@login_required
def editpermissions():
    username = session['username']
    permissions = db_manager.getPermissions(username)
    return render_template("friends.html", isLogin=False, friends="active", edit=True, permissions=permissions.items())

@app.route("/addfriends")
@login_required
def addfriends():
    return render_template("addfriends.html", isLogin=False, addfriends="active")

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
