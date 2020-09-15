from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask import jsonify
from flask import current_app as app


bp = Blueprint('message', __name__, url_prefix='/message')


class Message:
    def home_intro(self):
        return '<p><b>Pythia</b> is a web application developed as an \
        initiative for helping researchers to build labeled dataset  \
        with minimal effort by assigning annotators.\
        </p>\
        <h4>It supports</h4>\
        \
        <div style="margin-left: 20px;">\
            <li>Text to text labeling.</li>\
            <li>Multiple annotators for simultaneous annotation.</li>\
            <li>Tracking project progress.</li>\
            <li>Pause and resume ongoing project.</li>\
        </div>\
        <br> \
        <div>\
        Refer to\
        <a href="https://github.com/mehdirahman88/pythia/blob/master/README.md"> \
        README Pythia</a> for more details.\
        </div>'
