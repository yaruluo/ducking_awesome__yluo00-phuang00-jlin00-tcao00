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
        return redirect('/home')
    return dec

#====================================================

@app.route("/")
def root():
    return "ROOT PAGE"

if __name__ == "__main__":
    app.debug = True
    app.run()
