from app import db
import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String())
    slack_id = db.Column(db.String())
    display_name = db.Column(db.String())

    def __init__(self, spotify_id, slack_id, display_name):
        self.spotify_id = spotify_id
        self.slack_id = slack_id
        self.display_name = display_name

    def __repr__(self):
        return '<User {}>'.format(self.display_name)

class LastRefreshTime(db.Model):
    __tablename__ = 'last_refresh_time'
    id = db.Column(db.Integer, primary_key=True)
    previous_refresh = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)