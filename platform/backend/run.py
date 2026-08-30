from app import create_app, db
from app.routes import globals
from atlas_assistant.assistant import ChatSession
import logging

app = create_app()


# Configure Flask logger
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    # Set up log file, max 10MB, keep 3 backups
    file_handler = RotatingFileHandler(
        'flask.log', maxBytes=1024 * 1024 * 10, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask application startup')

# Initialize database and create tables
with app.app_context():
    db.create_all()

    globals.chat_session = ChatSession()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
