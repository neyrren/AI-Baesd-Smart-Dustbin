from flask import Flask
import os

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    from .database import init_db
    init_db()

    from .routes import register_routes
    register_routes(app)

    return app