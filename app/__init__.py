from flask import Flask, Config


def create_app(config: Config = None) -> Flask:
    # Flask app
    app = Flask(__name__)

    if config is None:
        app.config.from_pyfile('config.py')
    else:
        config.from_mapping(config)

    # Blueprints
    from .view import view
    from .api import api
    app.register_blueprint(view)
    app.register_blueprint(api, url_prefix='/api')

    # Flask login
    from .login import login_manager
    login_manager.init_app(app)

    # DB config
    from .db import db
    db.init_app(app)

    return app
