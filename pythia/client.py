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
from pythia.db import get_db

import sqlite3
import csv
import os

bp = Blueprint('client', __name__, url_prefix='/client')


@bp.route('project/csv/<int:id>', methods=['GET','POST'])
def ret_project_csv(id):
    db = get_db()
    rows = {}
    try:
        with db:
            rows = db.execute(
                'SELECT "content_element", "label" from "contents"'
                '   WHERE "project_id"=?;',
                (id,)
            ).fetchall()
    except sqlite3.Error as e:
        return "Error(1): " + str(e.args[0])
    rows = get_json_from_table(rows)

    filename = "{}{}".format(id,"_labeled.csv")
    filedir = app.config['FILE_DIR_ABS']

    # with open(app.config['FILE_DIR']+filename, 'w') as csvfile:
    try:
        with open(filedir+filename, 'w') as csvfile:
            fieldnames = ['content_element', 'label']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return send_from_directory(directory=filedir,filename=filename, as_attachment=True)
    except:
        return "Error(2) Unknown: Exporting .csv"

@bp.route('project/json/<int:id>', methods=['GET','POST'])
def ret_project_json(id):
    db = get_db()
    rows = {}
    try:
        with db:
            rows = db.execute(
                'SELECT "content_element", "label" from "contents"'
                '   WHERE "project_id"=?;',
                (id,)
            ).fetchall()
    except sqlite3.Error as e:
        return "Error(1): " + str(e.args[0])
    rows = get_json_from_table(rows)
    return jsonify(rows)

@bp.route('/dashboard', methods=('GET', 'POST'))
@login_auth_required
def dashboard():
    return render_template('client/dashboard.html')

@bp.route('/home', methods=['GET', 'POST'])
@login_auth_required
def home():
    db = get_db()
    rows = []
    cur_date_time = db.execute("SELECT datetime('now')").fetchone()[0]
    active_id = []
    past_id = []
    try:
        rows = db.execute(
            'SELECT * FROM "projects"'
            '   WHERE client_id=?',
            (g.userid,)
        ).fetchall()
    except sqlite3.Error as e:
        return "Error(1): " + str(e.args[0])

    for row in rows:
        if row['due_date_time'] > cur_date_time:
            active_id.append((row['id'], row['title']))
        else:
            past_id.append((row['id'], row['title']))

    return render_template('client/home.html', active_id = active_id, past_id = past_id)

@bp.route('/createnew', methods=('GET', 'POST'))
@login_auth_required
def createnew():
    db = get_db()

    if request.method == 'GET':
        row = []
        annotator_info_list = []
        try:
            rows = db.execute(
                'SELECT "id", "username" FROM "users"'
                '   WHERE "user_type" = ?',
                ("Annotator",)
            ).fetchall()
        except sqlite3.Error as e:
            return "Error(1): " + str(e.args[0])

        rows = get_json_from_table(rows)

        if len(rows) == 0:
            annotator_info_list = []
        else:
            annotator_info_list = rows
        # return jsonify(annotator_info_list)

        return render_template('client/createnew.html', \
        annotator_info_list = annotator_info_list, max_annotator = app.config['MAX_ANNOTATOR'])

    if request.method == 'POST':

        ## Converting from from request object to dictionary
        myform = {}
        for x in request.form:
            myform[x] = request.form.getlist(x)
        # return jsonify(type(myform['annotator_id_list'][0]) is int)

        annotator_count = len(myform['annotator_id_list'])

        ## project_id: after successful insertion in projects
        #this should be latest project_id applicable for other tables
        ## project_id = get_table_size("projects") + 1 (wrong: db doesn't ensure
        #sequential increament of primary key)
        row = {}
        try:
            with db:
                row = db.execute(
                    'SELECT "seq" FROM "sqlite_sequence"'
                    '   WHERE "name" = ?;',
                    ("projects",)
                ).fetchone()
        except sqlite3.Error as e:
            return "Error(2) while reading sqlite_sequence: " + str(e.args[0])
        project_id = 1
        if row is not None:
            project_id = int(row['seq']) + 1

        ## Build query list for contributors
        contributor_query_list = []
        contributor_query_list.append((g.userid, project_id))
        for annotator in myform['annotator_id_list']:
            contributor_query_list.append((int(annotator), project_id))
        # return "{}{}".format((type(contributor_query_list[0][0]) is int), contributor_query_list)

        ## File Processing + Query Building for contents
        try:
            file = request.files['samplefile']
            file.filename = "{}{}".format(project_id,".csv")
            file.save(app.config['FILE_DIR_ABS']+file.filename)
        except Exception as e:
            return "Error(3) while reading or saving file: " + str(e.args[0])

        ## Build query list for contents
        content_query_list = []
        try:
            with open(app.config['FILE_DIR_ABS']+file.filename) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    content_query_list.append((project_id, row['Sample']))
        except Exception as e:
            return "Error(4) while reading File(csv): " + str(e.args[0])

        sample_size = len(content_query_list)

        try:
            with db:
                ## Save To Table: projects
                #Note: db AUTOINCREMENT doesn't ensure consecutity primary key
                #but we need the latest primary key for other tables
                #hence, passing the id parameter
                db.execute(
                    'INSERT INTO "projects" (id, client_id, title, description, due_date_time, \
                    label_count, label_list, annotator_count, annotator_id_list)'
                    '   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (project_id, g.userid, myform['title'][0], myform['description'][0], myform['due_date'][0] + " 23:59:59", \
                    myform['label_count'][0], myform['label_list'][0], annotator_count, ' '.join(myform['annotator_id_list']))
                )
                ## Save To Table: contributors
                db.executemany(
                    'INSERT INTO "contributors" ("user_id", "project_id")'
                    '   VALUES (?, ?);',
                    contributor_query_list
                )
                ## Save To Table: contents
                #Note: status by default "Not Annotated"
                db.executemany(
                    'INSERT INTO contents (project_id, content_element)'
                    '   VALUES (?, ?);',
                    content_query_list # Edit for full list insert
                )
                ## Updating "projects" status after successful insertions
                db.execute(
                    'UPDATE "projects"'
                    '   SET "status"=?, "sample_size"=?'
                    '   WHERE "id"=?;',
                    ("Uploaded", sample_size, project_id)
                )
        except sqlite3.Error as e:
            return "Error(5): " + str(e.args[0])
        except Exception as e:
            return "Error(6): " + str(e.args[0])
        # return "good"

        flash("Created New Successfully.")
        return redirect(url_for('client.home'))

@bp.route('/project/<int:id>', methods=('GET', 'POST'))
@login_auth_required
def project(id):
    ## Common Repetitive Tasks
    db = get_db()
    row = {}
    try:
        row = db.execute(
            'SELECT * from "projects"'
            '   WHERE "id" = ?;',(id,)
        ).fetchone()
    except sqlite3.Error as e:
        return "Error(1) while Fetching Project: " + str(e.args[0])
    if row == None:
        msg = "Weird! Project No. {} Not Found in DB".format(id)
        # flash("Weird! Project No. {} Not Found in DB".format(id))
        return render_template('client/project.html', project_id = id, info=None, msg = msg)
    ## END Common Repetitive Taskss

    if request.method == 'POST':
        ## Check if the request came from forms
        if request.form['button'] == 'secret':
            status = row['status']
            if status == "Not Uploaded":
                flash('Project Status Must Be "Uploaded"')
                return redirect(url_for("client.project", id = id))
            elif status == "Uploaded":
                cur_date_time = get_current_date_time(db)
                if cur_date_time >= row['due_date_time']:
                    return redirect(url_for("client.project", id = id))

                try:
                    with db:
                        db.execute(
                            'UPDATE "projects"'
                            '   SET "status"=?'
                            '   WHERE "id"=?;',("Running", id)
                        )
                        flash("Project Started.")
                        return redirect(url_for("client.project", id = id))
                except sqlite3.Error as e:
                    return "Error(2): " + str(e.args[0])
            else:
                flash("No Action.")
                return redirect(url_for("client.project", id = id))

        if request.form['button'] == 'secret2':
            if row['status'] == "Running":
                try:
                    with db:
                        db.execute(
                            'UPDATE "projects"'
                            '   SET "status"=?'
                            '   WHERE "id"=?;',("Uploaded", id)
                        )
                    flash('Project Stopped.')
                    return redirect(url_for("client.project", id = id))
                except sqlite3.Error as e:
                    return "Error(3): " + str(e.args[0])
            else:
                flash('No Actions')
                return redirect(url_for("client.project", id = id))

        return jsonify("Error-")

    if request.method == 'GET':
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
                return "Error(4): " + str(e.args[0])
        ## status might get updated,
        #so saving one query for row = updated fetch,
        #passing the variable status1 specially
        flash("Project Status: " + status1)
        return render_template('client/project.html', project_id = row['id'], info=row, \
        status = status1, progress=progress, msg = None)
