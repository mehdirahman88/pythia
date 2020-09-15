import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        FILE_DIR='./files/',
        FILE_DIR_ABS=os.path.join(app.root_path, '../files/'),
        DATABASE=os.path.join(os.path.join(app.root_path, '../files/'), 'db.sqlite'),
        DEBUG_VIEWS=False,
        MAX_DISPATCH=5,
        MAX_ANNOTATOR=10,
    )

    try:
        print("Creating: {}".format(app.config['FILE_DIR_ABS']))
        os.makedirs(app.config['FILE_DIR_ABS'])
        
    except Exception as e:
        print(e.args[1])

    from . import db
    db.init_app(app)

    # Register Blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import client
    app.register_blueprint(client.bp)

    from . import annotator
    app.register_blueprint(annotator.bp)

    from . import message
    app.register_blueprint(message.bp)

    from . import utilsmy
    app.register_blueprint(utilsmy.bp)

    from . import dispatcher
    app.register_blueprint(dispatcher.bp)

    from . import testing
    app.register_blueprint(testing.bp)

    # Root path
    @app.route('/')
    def hello():
        return render_template('home.html', Message=message.Message());

    return app
