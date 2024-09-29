import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__name__))
load_dotenv('.env')


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    HOSTNAME = os.environ.get('HOSTNAME')
    SERVER_PORT = os.environ.get('SERVER_PORT')
    DB_PORT = os.environ.get('DB_PORT')
    USERNAME = os.environ.get('USERNAME')
    PASSWORD = os.environ.get('PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{
        USERNAME}:{PASSWORD}@{HOSTNAME}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = False
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
