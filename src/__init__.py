# Main imports
import os, sys

# Logging
import logging

# Flask
from flask import Flask
from flask import render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder="../templates")
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Set up logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(format='%(asctime)s: %(name)s:%(message)s', level=log_level)
    logging.log(100, f"Setting up application. Logging level={log_level}")
    logging.basicConfig(format='%(asctime)s: %(levelname)s:%(name)s:%(message)s', level=log_level)

    @app.route('/')
    def root():
        return render_template("index.html")

    return app
