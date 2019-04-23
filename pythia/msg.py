from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask import jsonify
from flask import current_app as app

bp = Blueprint('msg', __name__, url_prefix='/message')
