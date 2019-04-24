from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify
from flask import current_app as app

from pythia.auth import get_current_date_time, get_json_from_table, get_progress, login_auth_required
from pythia.db import get_db
from pythia.dispatcher import get_data, push_data

import sqlite3
import functools

# rom pythia.dispatcher import

bp = Blueprint('annotator', __name__, url_prefix='/annotator')


@bp.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
    return render_template('annotator/dashboard.html')

@bp.route('/home', methods=('GET', 'POST'))
@login_auth_required # Note: not only login required
def home():
    db = get_db()
    cur_date_time = get_current_date_time(db)

    rows = []
    # rows = ["Helloo"]
    # Get active projects for the user (annotator)
    try:
        rows = db.execute(
            'SELECT contributors.project_id, projects.title'
            '   FROM contributors'
            '       INNER JOIN projects ON contributors.project_id = projects.id'
            '       WHERE contributors.user_id = ? AND projects.due_date_time > ?;',
            (g.userid, cur_date_time)
        ).fetchall()
    except sqlite3.Error as e:
        return e.args[0]

    rows = get_json_from_table(rows)
    # rows.append(g.userid)
    # return jsonify(rows)

    return render_template('annotator/home.html', active_id = rows)

def pre_actions(view):
    @functools.wraps(view)
    def wrapped_view(*nargs, **kwargs):
        id = kwargs['id']
        db = get_db()
        row = {}
        try:
            row = db.execute(
                'SELECT * from "projects"'
                '   WHERE "id" = ?;',(id,)
            ).fetchone()
        except sqlite3.Error as e:
            return e.args[0]
        if row == None:
            msg = "Weird! Project No. {} Not Found in DB".format(id)
            return render_template('annotator/error.html', msg = msg)

        if row['status'] != 'Running':
            flash("Project Not Running. Status: "  + row['status'])
            return render_template('annotator/error.html')

        status0 = row['status']
        status1 = row['status']

        cur_date_time = get_current_date_time(db)
        progress = get_progress(id)
        if cur_date_time >= row['due_date_time']:
            status1 = "Time Out"

        if row['sample_size'] == progress:
            status1 = "Completed"

        if status0 != status1:
            try:
                with db:
                    db.execute(
                        'UPDATE "projects"'
                        '   SET "status"=?'
                        '   WHERE "id"=?;',(status1, id)
                    )
            except sqlite3.Error as e:
                return e.args[0]
            flash("Project Status: " + status1)
            return render_template('annotator/home.html', project_id=id)

        return view(*nargs, **kwargs) #Pass To Main View
    return wrapped_view

@bp.route('/project/<int:id>', methods=('GET', 'POST'))
@login_auth_required
@pre_actions
def project(id):
    if request.method == 'GET':
        #return "Service Down!"
        table_content = get_data(id)

        row = {}
        db = get_db()
        try:
            with db:
                row = db.execute(
                    'SELECT "label_list", "description" FROM "projects"'
                    '   WHERE "id" = ?;',
                    (id,)
                ).fetchone()
        except sqlite3.Error as e:
            return e.args[0]


        desc = row['description']
        sample_list = []
        for content in table_content:
            sample_list.append((content['id'], content['content_element']))
        label_list = []
        # for label in row['label_list']:
        labels = row['label_list'].split(" ")
        # return jsonify(labels) # test
        for label in labels:
            label_list.append(label)

        # test
        # return render_template('annotator/project.html', project_id=id, \
        # max_annotation = 2, sample_list = ['sample1', 'sample2', 'sample3'], \
        # label_list = ['label1', 'label2', 'label3', 'label4', 'label5', 'label6'], desc = "The quick brown fox")
        return render_template('annotator/project.html', project_id=id, \
        max_annotation = 1, sample_list = sample_list, \
        label_list = label_list, desc = desc)

    if request.method == 'POST':
        myform = {}
        data = []
        for x in request.form.keys():
            data.append((x, " ".join(request.form.getlist(x))))
            # myform[x] = request.form.getlist(x)
        # return jsonify(myform.keys()) #Error not json serialzable
        # return jsonify(list(myform.keys()))

        # Content Ids are return in this fashion from the view
        # content_ids = list(myform.keys())
        sz_success = push_data(data)

        flash("Success In {} Annotations.".format(sz_success))
        return redirect(url_for('annotator.project', id = id))
