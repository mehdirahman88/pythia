import os

from flask import Flask, render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        FILE_DIR='./files/',
        FILE_DIR_ABS=os.path.join(app.root_path, '../files/'),
        DATABASE='./files/'+'pythia.sqlite', #os.path.join(app.instance_path, 'testappdb1.sqlite'),
        DEBUG_VIEWS = False,
        MAX_DISPATCH = 5,
        MAX_ANNOTATOR = 10,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.config['FILE_DIR_ABS'])
    except OSError:
        pass

    # Note: Initiating DB
    from . import db
    db.init_app(app)

    # Note: Registering To Blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import client
    app.register_blueprint(client.bp)

    from . import annotator
    app.register_blueprint(annotator.bp)

    from . import msg
    app.register_blueprint(msg.bp)

    from . import utilsmy
    app.register_blueprint(utilsmy.bp)

    from . import dispatcher
    app.register_blueprint(dispatcher.bp)

    from . import testing
    app.register_blueprint(testing.bp)

    # Note: Fix the root path
    @app.route('/')
    def hello():
        return render_template('home.html', MSG=msg.MSG());
    # app.add_url_rule('/', endpoint='index')

    return app
