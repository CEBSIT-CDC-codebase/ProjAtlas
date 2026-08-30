from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:{}@{}:{}/{}'.format(os.getenv(
        'DB_PASSWORD'), os.getenv('DB_HOST'), os.getenv('DB_PORT'), os.getenv('DB_DATABASE'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
