import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex()
    COLLAB_ADMIN = 'mish030206@gmail.com'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


    @staticmethod
    def init_app(app):
        pass

class DockerConfig(Config):
    NAME = 'docker'

    @classmethod
    def init_app(cls, app):
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'docker': DockerConfig,

    'default': Config
}
