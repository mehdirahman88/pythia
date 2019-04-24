from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask import jsonify
from flask import current_app as app

bp = Blueprint('msg', __name__, url_prefix='/message')

class MSG:
    def home_intro(self):
        return '<p><b>Pythia</b> is a web application primarily developed as an \
        initiative for helping researchers to build <i>Labeled Dataset</i> from \
        crowd in a organized way, with minimal effort, and yet with reliability.\
        </p>\
        <h4>Features</h4>\
        \
        <div style="margin-left: 20px;">\
            <li>Text to text labeling</li>\
            <li>Allow multiple annotators for simultaneous Annotation</li>\
            <li>View project progress status</li>\
            <li>Pause and resume running project</li>\
        </div>\
        <br> \
        <div>\
        Refer to\
        <a href="https://github.com/mehdirahman88/pythia/blob/master/README.md"> \
        README Pythia</a> for more details.\
        </div>'
