# Project Journie by Team Ducking Awesome


Team Ducking Awesome

SoftDev pd1

P05: Fin

2020-06-11


# Roster
Yaru (PM)
- Oversees & plans incremental project development milestones
- Updates design doc and devlog
- Instructions page

Peihua Huang
- Create HTML form that takes user input and stores tracker data in database (using either D3 or Bootstrap)
- Representation of monthly tracker data in calendars using D3
- Implement commenting feature on journal entries by friends

Jackie Lin
- Login/signup feature
- Flask routing 
- Implement searching for and adding friends feature
- Allow user to set global viewing permissions for friends 

Tiffany Cao
- Frontend (creation and styling of HTML pages)
- Implement daily journal entry and to-do list feature


# Description/Summary

Our app intends to recreate the bullet journaling experience online, and add a collaborative aspect to it. Through our app, people will be able to write daily entries and keep track of things in their daily lives like their mood and their sleep schedule. People will also be able to keep up with their friends’ daily lives by viewing and commenting on each others’ journals to keep social interaction alive during quarantine! 

## Instructions

### Assuming python3 and pip are already installed

### Virtual Environment

- To prevent conflicts with globally installed packages, it is recommended to run everything below in a virtual environment.

Set up a virtual environment by running the following in your terminal:

```shell
python3 -m venv hero
# replace hero with anything you want
# If the above does not work, run with python3 (this may be the case if a version of python2 is also installed)
```

To enter your virtual environment, run the following:

```shell
. hero/bin/activate
```

To exit your virtual environment, run the following:

```shell
deactivate
```

### Dependencies

Run the following line in your virtual environment

```shell
pip install -r requirements.txt
```

### Cloning

Run the following line in your terminal

```shell
git clone https://github.com/yaruluo/ducking_awesome__yluo00-phuang00-jlin00-tcao00
```

### Running

Run the following line in your virtual environment

```shell
python3 app/__init.py__
```

Open a browser and head to <http://127.0.0.1:5000/>
