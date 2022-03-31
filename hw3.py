import string
from flask import Flask, send_from_directory, render_template, request, redirect, url_for, flash, session
from flask_httpauth import HTTPBasicAuth
from pymongo import MongoClient

app = Flask(__name__)

auth = HTTPBasicAuth()
client = MongoClient('localhost', 27017)
db = client.wad

app.secret_key = 'OgrywtIr'
app.config['SESSION_TYPE'] = 'filesystem'

@auth.verify_password
def verify_password(username: string, password: string):
    if db.users.find_one({'username': username, 'password': password}) is not None:
        return db.users.find_one({'username': username, 'password': password})
    else:
        return False

def create_user(username: string, password: string):
    db.users.insert_one(
        {
            'username': username,
            'password': password
        }
    )

@app.route('/', methods=["GET"])
def index():    return render_template("index.html")

@app.route('/auth', methods=["GET", "POST"])
def auth():
    if request.method == "GET":
        return render_template("auth.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get('password')
        user = verify_password(username, password)
        if user != False:
            session['username'] = user.get('username')
            return redirect(url_for('profile'))
        else:
            flash('Wrong credentials')
            return redirect(url_for('auth'))

@app.route('/profile', methods=["GET", "POST"])
def profile():
    if session['username']:
        username = session['username']
        if request.method == "GET":
            return render_template('cabinet.html',username=username)
        else:
            title = request.form.get('title')
            content = request.form.get('note')

            db.notes.insert_one({
                'title': title,
                'content': content
            })
            flash("New story added!")
            return redirect('/stories')
    else:
        return redirect(url_for('auth'))

@app.route("/logout", methods=["GET"])
def logout():
    session['username'] = None
    return redirect(url_for('index'));

@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template("/signup.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get('password')
        if verify_password(username, password) != False:
            flash('This user already exist')
            return redirect(url_for('auth'))
        else:
            create_user(username, password)
            return redirect(url_for('auth'))

@app.route('/stories', methods=['GET'])
def show_stories():
    notes = list(db.notes.find({}))
    return render_template('/stories.html', notes=notes)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
