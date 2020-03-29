import os

class Config(object):
    SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID', None)
    SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET', None)
    SPOTIFY_ACCESS_TOKEN = os.environ.get('SPOTIFY_ACCESS_TOKEN', None)

    SLACK_REQUEST_TOKEN = os.environ.get('SLACK_REQUEST_TOKEN', None)
    SLACK_TEAM_ID = os.environ.get('SLACK_TEAM_ID', None)
    SLACK_BOT_ADMIN = os.environ.get('SLACK_BOT_ADMIN', None)

    CHART_STUDIO_KEY = os.environ.get('CHART_STUDIO_KEY', None)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', None)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
