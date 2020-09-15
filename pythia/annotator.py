import sqlite3
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask import jsonify
from flask import current_app as app

from pythia.auth import login_auth_required
from pythia.utilsmy import get_current_date_time, get_json_from_table, get_progress
from pythia.db import get_db
from pythia.dispatcher import get_data, push_data


bp = Blueprint('annotator', __name__, url_prefix='/annotator')


@bp.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
    return render_template('annotator/dashboard.html')


@bp.route('/home', methods=('GET', 'POST'))
@login_auth_required
def home():
    db = get_db()
    cur_date_time = get_current_date_time(db)

    # Get active projects for the user (annotator)
    rows = {}
    try:
        rows = db.execute(
            'SELECT contributors.project_id, projects.title'
            '   FROM contributors'
            '       INNER JOIN projects ON contributors.project_id = projects.id'
            '       WHERE contributors.user_id = ? AND projects.due_date_time > ?;',
            (g.userid, cur_date_time)
        ).fetchall()
    except sqlite3.Error as e:
        return "Error(1): " + str(e.args[0])

    rows = get_json_from_table(rows)
    # rows.append(g.userid)
    # return jsonify(rows)

    return render_template('annotator/home.html', active_id = rows)


# Decorator: Checks for the Live status of the project
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
            return "Error(1): " + str(e.args[0])
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
                return "Error(2): " + str(e.args[0])
            flash("Project Status: " + status1)
            return render_template('annotator/home.html', project_id=id)

        return view(*nargs, **kwargs) #Pass To Main View
    return wrapped_view


@bp.route('/project/<int:id>', methods=('GET', 'POST'))
@login_auth_required
@pre_actions
def project(id):
    if request.method == 'GET':
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
            return "Error(1): " + str(e.args[0])

        description = row['description']
        sample_list = []
        for content in table_content:
            sample_list.append((content['id'], content['content_element']))
        label_list = []
        labels = row['label_list'].split(" ")
        for label in labels:
            label_list.append(label)

        return render_template('annotator/project.html',
                                project_id=id,
                                max_annotation=1,
                                sample_list=sample_list,
                                label_list=label_list,
                                description=description)

    if request.method == 'POST':
        myform = {}
        data = []
        for x in request.form.keys():
            data.append((x, " ".join(request.form.getlist(x))))

        sz_success = push_data(data)

        flash("Success In {} Annotations.".format(sz_success))
        return redirect(url_for('annotator.project', id = id))
