__author__ = 'Daniel'
from gevent.pywsgi import WSGIServer
import threading
from flask import Flask, render_template, Response, url_for, request, redirect
from flask_login import LoginManager, login_user, login_required, current_user
import os
import sqlite3

USERNAME_ELEMENT = 'username'
PASSWORD_ELEMENT = 'password'
WEB_SERVER_PORT = 5000
CURRENT_WORKING_DIRECTORY = os.getcwd()  # Gives easy access to our server's files' path.
CODE_FILES_PATH = CURRENT_WORKING_DIRECTORY + '\\Templates\\'  # The path to where all the server files are saved at
DB_PATH = CODE_FILES_PATH + 'userbase.db'

# Starts the flask app.
app = Flask(__name__)
app.debug = True
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    """
    Renders the homepage.
    """
    return render_template('index.html')


@app.route('/submit_login', methods=['POST'])
def submit_login():
    """
    Extracts the username and password inserted by the user. Checks if the user exists in the database and if he does
    checks if the password that was inserted by the user is correct.
    """
    username = request.form[USERNAME_ELEMENT]
    password = request.form[PASSWORD_ELEMENT]
    if validate_login(username, password):
        user = User(username, password)
        login_user(user)
        return render_template('successful_login.html')
    return render_template('log_in.html')


def validate_login(username, password):
    """
    username: String: the username of the user
    password: String: the password that the user entered.

    Validates if the username and password belong to an existing user and are both correct. Returns True if the user
    has been validated and False otherwise.
    """
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (username,))
    password2 = cur.fetchone()
    db.close()
    if password2 is None:
        return False
    if password2[0] == password:
        return True
    return False


@login_manager.user_loader
def user_loader(user_id):
    """
    user_id: unicode: username used to make the corresponding User object

    Given *user_id*, return the associated User object.
    this is set as the user_loader for flask-login. It uses it to retrieve a User object which it then uses for
    everything.
    if no user can be made (e.g invalid user_id), it returns None. (This is specified by flask-login as the type to
    return if no User object can be made)
    """
    return make_user(str(user_id))


def make_user(user_id):
    """
    user_id: String: username used to make the corresponding User object

    Given *user_id*, return the associated User object.
    Creates the User object associated with user_id. If no User object can be made, returns None.
    """
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (user_id,))
    password = cur.fetchone()
    db.close()
    if password is None:
        return None
    return User(user_id, password[0])


@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    """
    Extracts the username and password inserted by the user. Checks if the user already exists and if he doesn't, adds
    him to the user database.
    """
    username = request.form[USERNAME_ELEMENT]
    password = request.form[PASSWORD_ELEMENT]
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user_data = cur.fetchone()
    if user_data is None:  # Checks if the username inserted already exists in the database
        cur.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (username, password, DEFAULT_INFO, DEFAULT_INFO, DEFAULT_INFO, DEFAULT_INFO))
        db.commit()
        db.close()
        return render_template('successful_signup.html')
    else:
        print user_data
        db.close()
        return render_template('user_already_exists.html')


@app.route("/log_in")
def log_in():
    """
    Generates the log in page.
    """
    return render_template('log_in.html')

if __name__ == "__main__":
    thread = threading.Thread(target=SettingsAndNotificationReceiver().start_server)
    thread.daemon = True
    thread.start()
    app.config["SECRET_KEY"] = "ITSASECRET"
    http = WSGIServer(('', WEB_SERVER_PORT), app)
    http.serve_forever()
