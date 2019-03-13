import sqlite3
import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify


# Static config
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'not-so-secret-at-all-really'
USERNAME = 'admin'
PASSWORD = 'admin'


# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__)


# Connect to DB
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# Create the DB
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# Reference DB and connect if not connected
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# Close connection to DB
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    """Comb the DB for entries and display them"""
    db = get_db()
    cur = db.execute('SELECT * FROM entries ORDER BY id desc')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User auth / session management"""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """User logout / session management"""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
    """Add new entry to the DB"""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute(
        'INSERT INTO entries (title, text) VALUES (?,?)',
        [request.form['title'], request.form['text']]
    )
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))


@app.route('/delete/<post_id>', methods=['GET'])
def delete_entry(post_id):
    """Remove an entry from the DB"""
    result = {'status': 0, 'message': 'Error'}
    try:
        db = get_db()
        db.execute('DELETE FROM entries WHERE id=' + post_id)
        db.commit()
        result = {'status': 1, 'message': 'Post deleted'}
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}

    return jsonify(result)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port='8888')
