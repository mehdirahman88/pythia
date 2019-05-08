from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify
from flask import current_app as app

from pythia.db import get_db, init_db

import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')


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

## Used Accross Modules
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*nargs, **kwargs):
        if g.username is None:
            return redirect(url_for('auth.signin'))
        return view(*nargs, **kwargs)
    return wrapped_view

## Implement This With + Without parameter *
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
                return "Error(1): " + str(e.args[0])
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


## Routes of Auth Module
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
            return "Error(1): " + str(e.args[0])

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
                return "Error(2): " + str(e.args[0])
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
            return "Error(1): " + str(e.args[0])

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
