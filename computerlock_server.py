__author__ = 'Daniel'
from gevent.pywsgi import WSGIServer
import threading
from user_class import User
import setting_parser
from flask import Flask, render_template, Response, url_for, request, redirect
from flask_login import LoginManager, login_user, login_required, current_user
import os
import sqlite3
import json

USERNAME_ELEMENT = 'username'
PASSWORD_ELEMENT = 'password'
ADDED_SETTINGS_ELEMENT = 'added-settings'
WEB_SERVER_PORT = 5000
CURRENT_WORKING_DIRECTORY = os.getcwd()  # Gives easy access to our server's files' path.
CODE_FILES_PATH = CURRENT_WORKING_DIRECTORY + '\\Templates\\'  # The path to where all the server files are saved at
DB_PATH = CODE_FILES_PATH + 'userbase.db'
MIMETYPES = {'css': 'text/css', 'png': 'image/png', 'ttf': 'application/x-font-ttf '}
EXTENSION_ELEMENT = 1
PROCESS_TUPLE = 0
PATHS_TUPLE = 1
EXTENSION_TUPLE = 2
DEFAULT_DB_VALUE = ''

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
    Validates if the username and password belong to an existing user and are both correct.
    
    :param username: String: the username of the user
    :param password: String: the password that the user entered.
    
    :returns True if the user has been validated and False otherwise
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
    Given :param user_id, return the associated User object.
    this is set as the user_loader for flask-login. It uses it to retrieve a User object which it then uses for
    everything.
    if no user can be made (e.g invalid user_id), it returns None. (This is specified by flask-login as the type to
    return if no User object can be made)
    
    :param user_id: unicode: username used to make the corresponding User object
    :returns the User object associated with :param user_id. If no user can be made, :returns None
    
    """
    return make_user(str(user_id))


def make_user(user_id):
    """
    Creates the User object associated with user_id.
    
    :param user_id: String: username used to make the corresponding User object
    :returns the User object associated with :param user_id. If no User object can be made, :returns None
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
        cur.execute("INSERT INTO users VALUES (?,?,?,?,?)", (username, password, DEFAULT_DB_VALUE, DEFAULT_DB_VALUE, DEFAULT_DB_VALUE))
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


@app.route("/sign_up")
def sign_up():
    """
    Generates the sign up page.
    """
    return render_template('sign_up.html')


@app.route("/settings")
@login_required
def settings():
    """
    Generates the settings page
    """
    return render_template('settings.html')


@app.route('/submit_file/<filename>')
def return_files(filename):
    """
    :param filename: String: the name of the file that is requested by the browser.

    :return: the file requested by the browser to the browser.
    """
    file_path = CODE_FILES_PATH + filename  # All of the web server's files are in CODE_FILES_PATH
    print file_path
    if os.path.isfile(file_path):
        print file_path
        with open(file_path, 'rb') as web_file:
            file_extension = os.path.splitext(file_path)[EXTENSION_ELEMENT]
            file_extension = file_extension.strip('.')  # Strips the file extension's redundant '.' in the beginning
            mimetype = MIMETYPES[file_extension]
            file_data = web_file.read()
            return Response(file_data + b'\r\n', mimetype=mimetype)
    return render_template('file_not_found.html')


@app.route("/add_settings", methods=['POST'])
@login_required
def add_settings():
    """
    Adds the settings received by the user to the database after making sure that the user entries are valid 
    (actual file paths/processes/etc)
    :return: the homepage
    """
    added_settings = request.form[ADDED_SETTINGS_ELEMENT]
    parsed_settings = setting_parser.parse_settings(added_settings)
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT processes, file_extensions, file_paths FROM users WHERE username=?", (current_user.id, ))
    row = cur.fetchone()
    processes, file_extensions, file_paths = row
    if parsed_settings[PROCESS_TUPLE][1]:  # this check makes it so a redundant \n wont be added to the database
        # we need to add an extra new line since join does not add a new line to the final element
        processes += '\n'.join(parsed_settings[PROCESS_TUPLE][1]) + '\n'
    if parsed_settings[EXTENSION_TUPLE][1]:
        file_extensions += '\n'.join(parsed_settings[EXTENSION_TUPLE][1]) + '\n'
    if parsed_settings[PATHS_TUPLE][1]:
        file_paths += '\n'.join(parsed_settings[PATHS_TUPLE][1]) + '\n'
    cur.execute("UPDATE users SET processes=?, file_extensions=?, file_paths=? WHERE username=?", (processes, file_extensions, file_paths, current_user.id))
    db.commit()
    db.close()
    return render_template('index.html')


@app.route("/remove_settings", methods=['POST'])
@login_required
def remove_settings():
    """
    Removes the settings specified by the user from the database (if the specified settings exist)
    :return: the homepage
    """
    return render_template('index.html')

if __name__ == "__main__":
    #  thread = threading.Thread(target=SettingsAndNotificationReceiver().start_server)
    #  thread.daemon = True
    #  thread.start()
    app.config["SECRET_KEY"] = "ITSASECRET"
    http = WSGIServer(('', WEB_SERVER_PORT), app)
    print "ok"
    http.serve_forever()
