from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask import jsonify
from flask import current_app as app

from pythia.db import get_db
from pythia.utilsmy import get_json_from_table

import sqlite3

bp = Blueprint('dispatcher', __name__, url_prefix='/dispatcher')


def get_data(project_id):
    n = app.config['MAX_DISPATCH']
    db = get_db()

    rows = {}
    try:
        with db:
            rows = db.execute(
                'SELECT * FROM "contents"'
                '   WHERE "project_id"=? AND "status"=?'
                '   LIMIT ?',
                (project_id, "Not Annotated", n)
            ).fetchall()
    except sqlite3.Error as e:
        return "Error(1): " + str(e.args[0])

    sz = len(rows)
    rows_final = rows

    ## Do not update now: it will make data Processing and get into next select

    sz2 = n - sz

    rows = {}
    if sz2 > 0:
        try:
            with db:
                rows = db.execute(
                    'SELECT * FROM "contents"'
                    '   WHERE "project_id"=? AND "status"=?'
                    '   LIMIT ?;',
                    (project_id, "Processing", sz2)
                ).fetchall()
        except sqlite3.Error as e:
            return "Error(2): " + str(e.args[0])

        rows_final += rows

    if len(rows_final) == 0:
        return "Project Complete"

    ## Update at end
    query_list = []
    for row in rows_final:
        query_list.append(("Processing", row['id']))
    # return jsonify(query_list)
    try:
        with db:
            db.executemany(
                'UPDATE "contents"'
                '   SET "status" = ?'
                '   WHERE "id" = ?;',
                query_list
            )
    except sqlite3.Error as e:
        return "Error(3): " + str(e.args[0])

    # if "test/get" in request.url:
    #     rows_final = get_json_from_table(rows_final)
    #     return jsonify(rows_final)
    return rows_final

def push_data(data):
    query_list = []
    for datum in data: #!!!
        if datum[1] != '*':
            query_list.append(("Annotated", datum[1], datum[0], "Processing"))
    # sz_success = len(query_list)

    db = get_db()
    rows = {}
    sz_success = 0
    try:
        with db:
            sz_success = db.executemany(
                'UPDATE "contents"'
                '   SET "status" = ?, "label" = ?'
                '   WHERE "id"  = ? AND "status" = ?;',
                query_list
            ).rowcount
    except sqlite3.Error as e:
        return "Error(1): " + str(e.args[0])
    # rows = get_json_from_table(rows)
    # return rows.rowcount
    return sz_success

@bp.route('test/get/<int:project_id>')
def test_get_data(project_id):
    return jsonify(get_json_from_table(get_data(project_id)))

@bp.route('test/push')
def test_push():
    data = []
    data.append((1, "red"))
    data.append((2, "green"))
    data.append((3, "blue"))
    return jsonify(push_data(data))
