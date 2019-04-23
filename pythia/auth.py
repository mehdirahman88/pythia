import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify
from flask import current_app as app

from pythia.db import get_db, init_db
bp = Blueprint('auth', __name__, url_prefix='/auth')

### Strictly Testing
@bp.before_app_request
def load_user():
    username = session.get('username')
    userid = session.get('userid')
    usertype = session.get('usertype')
    g.username = None
    g.userid = None
    g.usertype = None
    if username is not None:
        g.username = username
    if userid is not None:
        g.userid = userid
    if usertype is not None:
        g.usertype = usertype
    # if '/client' in request.path:
    #     g.user = "God_C"
    #     g.userid = 1
    # elif '/annotator' in request.path:
    #     g.user = "God_A"
    #     g.userid = 3
    # else:
    #     g.user = "Problematic User"

### Used Accross Modules
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*nargs, **kwargs):
        if g.username is None:
            return redirect(url_for('auth.signin'))
        return view(*nargs, **kwargs)
    return wrapped_view

### Implement This With + Without parameter *
def login_auth_required(view):
    @functools.wraps(view)
    def wrapped_view(*nargs, **kwargs):
        if g.username is None:
            session.clear()
            flash("who are you?")
            return redirect(url_for('auth.signin'))
        if g.userid is None:
            session.clear()
            flash("who are you?")
            return redirect(url_for('auth.signin'))

        id = kwargs.get('id')
        if id is not None:
            db = get_db()
            row = None
            try:
                with db:
                    row = db.execute(
                        'SELECT * FROM "contributors"'
                        '   WHERE "user_id" = ? AND "project_id" = ?;',
                        (g.userid, id)
                    ).fetchone()
            except sqlite3.Error as e:
                return e.args[0]
            if row is None:
                session.clear()
                flash("who are you?")
                return redirect(url_for('auth.signin'))
        if '/client' in request.url:
            if g.usertype != 'Client':
                session.clear()
                flash("who are you?")
                return redirect(url_for('auth.signin'))
        elif '/annotator' in request.url:
            if g.usertype != 'Annotator':
                session.clear()
                flash("who are you?")
                return redirect(url_for('auth.signin'))
        else:
            session.clear()
            flash("who are you?")
            return redirect(url_for('auth.signin'))
        return view(*nargs, **kwargs)
    return wrapped_view
### Routes of Auth Module

@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usertype = request.form['usertype']

        db = get_db()
        row = {}
        msg = ""
        try:
            with db:
                row = db.execute(
                    'SELECT * FROM "users"'
                    '   WHERE "username" = ?;',
                    (username,)
                ).fetchone()
        except sqlite3.Error as e:
            return e.args[0]

        if row is not None:
            msg = "User {} Already Exists.".format(username)
        else:
            try:
                with db:
                    db.execute(
                        'INSERT INTO "users" ("username", "password", "user_type")'
                        '   VALUES(?,?,?);',
                        (username, generate_password_hash(password), usertype)
                    )
                return redirect(url_for('auth.signin'))
            except sqlite3.Error as e:
                return e.args[0]
        flash(msg)
    return render_template('auth/signup.html')

@bp.route('/signout')
def signout():
    session.clear();
    g.pop('username', None)
    g.pop('userid', None)
    g.pop('usertype', None)
    flash("Successfully Signed Out")
    return redirect(url_for('hello'))

@bp.route('/signin', methods=('GET', 'POST'))
def signin():
    if request.method == 'GET':
        if g.username is None:
            return render_template('auth/signin.html')
        if g.usertype == 'Annotator':
            return redirect(url_for('annotator.home'))
        if g.usertype == 'Client':
            return redirect(url_for('client.home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password

        db = get_db()
        row = None
        msg = ""
        try:
            with db:
                row = db.execute(
                    'SELECT * FROM "users"'
                    '   WHERE "username" = ?;',
                    (username,)
                ).fetchone()
        except sqlite3.Error as e:
            return e.args[0]

        if row is None:
            msg = "User Not Found."
        elif not check_password_hash(row['password'], password):
            msg = "Incorrect Password."

        if msg == "":
            session['usertype'] = row['user_type']
            session['userid'] = row['id']

            if session['usertype'] == 'Annotator':
                return redirect(url_for('annotator.home'))
            if session['usertype'] == 'Client':
                return redirect(url_for('client.home'))
        flash(msg)
    return render_template('auth/signin.html')


### Routes For TESTING
@bp.route('/test', methods=('GET', 'POST'))
def test():

    return jsonify(generate_password_hash("123456"))

    import sqlite3
    init_db()

    db = get_db()

    xx=[]
    x = db.execute("SELECT datetime('now')").fetchone()
    xx.append(x[0])
    import time;
    time.sleep(3)
    x = db.execute('SELECT datetime("now")').fetchone()
    xx.append(x[0])
    # x = db.execute(
    #     "SELECT date('now')"
    # ).fetchall()
    xx.append(xx[0] < xx[1])
    xx.append(xx[0] > xx[1])

    return jsonify(xx)
    return render_template('auth/signin.html')


# Utilities
@login_auth_required # Note: Not necessary
def get_progress(id):
    '''
    Computes Progress of A Project

    Parameters:
    id - Project Id

    Returns:
    Progress(No. of Rows Annotated) of The Project
    '''
    ans = 0
    db = get_db()
    try:
        with db:
            ans = db.execute(
                'SELECT COUNT(*) from "contents"'
                '   WHERE "project_id" = ? and "status" = ?;',
                (id, "Annotated")
            ).fetchone()[0]
    except:
        ans = 9999999
    return ans
def get_table_size(tname):
    db = get_db()

    # Problematic? using {}
    try:
        x = db.execute('SELECT MAX(rowid) AS mxid FROM {}'.format(tname)).fetchone()
    except:
        return 0

    sz_projects = 0
    if x['mxid'] is not None:
        sz_projects = x['mxid']
    return sz_projects

def get_current_date_time(db):
    return db.execute("SELECT datetime('now')").fetchone()[0]

@bp.route('/populate_db', methods=('GET', 'POST'))
def populate_db():
    init_db()
    db = get_db()

    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('God_C', '1234', 'Client')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('mehdi_C', '1234', 'Client')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('God_A', '1234', 'Annotator')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('ann1', '1234', 'Annotator')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('ann2', '1234', 'Annotator')
    )

    cur_date_time_prev = db.execute("SELECT datetime('now', '-1 day')").fetchone()[0]
    cur_date_time_next = db.execute("SELECT datetime('now', '+1 day')").fetchone()[0]


    x = db.execute('SELECT MAX(rowid) AS mxid FROM "projects"').fetchone()
    sz_projects = 0
    if x['mxid'] is not None:
        sz_projects = x['mxid']

    db.execute(
        'INSERT into projects (client_id, title, description, due_date_time, \
        label_count, label_list, annotator_count, annotator_id_list)'
        '   VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
        (1, 'title', 'desc', cur_date_time_prev, 2, 'label1 label2', 3, '3 4 5')
    )
    sz_projects = sz_projects + 1
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (1, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (4, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (5, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (3, sz_projects)
    )

    db.execute(
        'INSERT into projects (client_id, title, description, due_date_time, \
        label_count, label_list, annotator_count, annotator_id_list)'
        '   VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
        (1, 'title', 'desc', cur_date_time_prev, 2, 'label1 label2', 3, '3 4 5')
    )
    sz_projects = sz_projects + 1
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (1, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (4, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (5, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (3, sz_projects)
    )

    db.execute(
        'INSERT into projects (client_id, title, description, due_date_time, \
        label_count, label_list, annotator_count, annotator_id_list)'
        '   VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
        (1, 'title', 'desc', cur_date_time_next, 2, 'label1 label2', 3, '3 4 5')
    )
    sz_projects = sz_projects + 1
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (1, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (4, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (5, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (3, sz_projects)
    )

    db.execute(
        'INSERT into projects (client_id, title, description, due_date_time, \
        label_count, label_list, annotator_count, annotator_id_list)'
        '   VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
        (1, 'title', 'desc', cur_date_time_next, 2, 'label1 label2', 3, '3 4 5')
    )
    sz_projects = sz_projects + 1
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (1, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (4, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (5, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (3, sz_projects)
    )

    db.execute(
        'INSERT into projects (client_id, title, description, due_date_time, \
        label_count, label_list, annotator_count, annotator_id_list)'
        '   VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
        (1, 'title', 'desc', cur_date_time_next, 2, 'label1 label2', 3, '3 4 5')
    )
    sz_projects = sz_projects + 1
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (1, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (4, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (5, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (3, sz_projects)
    )

    db.execute(
        'INSERT into projects (client_id, title, description, due_date_time, \
        label_count, label_list, annotator_count, annotator_id_list)'
        '   VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
        (2, 'title', 'desc', cur_date_time_prev, 2, 'label1 label2', 2, '4 5')
    )
    sz_projects = sz_projects + 1
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (2, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (4, sz_projects)
    )
    db.execute(
        'INSERT INTO "contributors" ("user_id", "project_id")'
        '   VALUES (?, ?);',
        (5, sz_projects)
    )
    # db.execute(
    #     'INSERT INTO "contributors" ("user_id", "project_id")'
    #     '   VALUES (?, ?);',
    #     (3, sz_projects)
    # )

    db.commit()
    flash("Succefully Populated: users, projects")
    return redirect(url_for('client.home'))

def edit(x):
    if len(x) == 0:
        return "Empty Table"
    keys = x[0].keys()

    resps = []
    for row in x:
        resp = {}
        for key in keys:
            resp[key] = row[key]
        resps.append(resp)
    return resps

### write help code
def get_json_from_table(x):
    '''
    Converts sqlite3 Table To JSON

    Parameters:
    -----------
    x - List of sqlite3 Row Objects


    Returns:
    --------
    Empty List - If len(x) == 0

    List Of JSON - When 'x' is a valid sqlite3 Row List, i.e. 'x[0].keys()' exists

    x (The Parameter Object Itself) - If 'x[0].keys()' does not exist

    '''

    if len(x) == 0:
        return []
    try:
        keys = x[0].keys()
    except:
        return x

    resps = []
    for row in x:
        resp = {}
        for key in keys:
            resp[key] = row[key]
        resps.append(resp)
    return resps
@bp.route('/show_db', methods=('GET', 'POST'))
def show_db():
    table = []

    db = get_db()

    rows = db.execute(
        'SELECT * FROM "users"'
    ).fetchall()

    table.append(edit(rows))

    rows = db.execute(
        'SELECT * FROM "projects"'
    ).fetchall()

    table.append(edit(rows))

    return jsonify(table)
