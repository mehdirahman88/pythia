import os
import sqlite3
import csv

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify
from flask import current_app as app
from flask import send_from_directory

from pythia.auth import login_required
from pythia.auth import login_auth_required
from pythia.utilsmy import get_table_size, get_current_date_time, get_progress, get_json_from_table
from pythia.db import get_db, init_db


bp = Blueprint('testing', __name__, url_prefix='/testing')


# Some Routes for RAW testing
#############################


@bp.route('/test', methods=('GET', 'POST'))
def test():
    return jsonify("hello");


@bp.route('/db/clear')
def db_clear():
    init_db()
    flash("DB Initialized")
    return redirect(url_for('hello'))


@bp.route('db/show/all')
def db_show_user():
    db = get_db()

    ROWS = []
    ROWS.append("Table: users")
    rows = {}

    try:
        with db:
            rows = db.execute(
                'SELECT * FROM "users"'
            ).fetchall()
    except sqlite3.Error as e:
        return e.args[0]

    rows = get_json_from_table(rows)
    ROWS.append(rows)

    return jsonify(ROWS)


@bp.route('/db/populate', methods=('GET', 'POST'))
def populate_db():
    init_db()
    db = get_db()

    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('God_C', generate_password_hash('1234'), 'Client')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('mehdi_C', generate_password_hash('1234'), 'Client')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('God_A', generate_password_hash('1234'), 'Annotator')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('ann1', generate_password_hash('1234'), 'Annotator')
    )
    db.execute(
        'INSERT INTO "users" ("username", "password", "user_type")'
        '   VALUES (?, ?, ?);',
        ('ann2', generate_password_hash('1234'), 'Annotator')
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


@bp.route('/db/show', methods=('GET', 'POST'))
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


@bp.route('/db/rollback', methods=('GET', 'POST'))
def db_rollback():
    return "success"
