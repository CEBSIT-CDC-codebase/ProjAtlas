from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # type: ignore
from config import Config
from flask_cors import CORS
from flask_executor import Executor

db = SQLAlchemy()
migrate = Migrate()
executor = Executor()


def create_app():
    app = Flask(__name__)
    executor.init_app(app)
    CORS(app)

    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import user_routes, session_routes, message_routes
    # Register blueprints
    app.register_blueprint(user_routes)
    app.register_blueprint(session_routes)
    app.register_blueprint(message_routes)

    return app
