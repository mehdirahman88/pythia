import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify
from flask import current_app as app

from pythia.db import get_db, init_db


bp = Blueprint('utilsmy', __name__, url_prefix='/utils')


def get_progress(id):
    '''
    Computes progress of a project

    Parameters:
    id : Project id

    Returns:
    Progress (No. of Rows Annotated) of the project
    '''
    db = get_db()
    ans = 0

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


def get_json_from_table(x):
    '''
    Converts sqlite3 Table To JSON

    Parameters:
    x : List of sqlite3 Row Objects


    Returns:
    Empty List : If len(x) == 0

    List Of JSON : If 'x' is a valid sqlite3 Row List, i.e. 'x[0].keys()' exists

    x (The parameter object itself) : If 'x[0].keys()' does not exist

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
