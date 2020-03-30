from slackapp import db
import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String())
    slack_id = db.Column(db.String())
    display_name = db.Column(db.String())
    is_admin = db.Column(db.Boolean())
    dev_access = db.Column(db.Boolean())
    prod_access = db.Column(db.Boolean())

    def __init__(self, spotify_id, slack_id, display_name):
        self.spotify_id = spotify_id
        self.slack_id = slack_id
        self.display_name = display_name

    def __repr__(self):
        return '<User {}>'.format(self.display_name)

class Config(db.Model):
    __tablename__ = 'configs'
    id = db.Column(db.Integer, primary_key=True)
    config_name = db.Column(db.String())
    value = db.Column(db.String())
    description = db.Column(db.Text())

    def __init__(self, config_name, value, description):
        self.config_name = config_name
        self.value = value
        self.description = description

    def __repr__(self):
        return '<Config {}>'.format(self.config_name)