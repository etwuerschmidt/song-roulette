import sys
sys.path.append('..')

from app import db, models
import json

with open('../users.json', 'r') as json_file:
    user_info = json.load(json_file)

for user in user_info:
    db_user = models.User(spotify_id=user, slack_id=user_info[user]['slack_id'], display_name=user_info[user]['name'])
    db.session.add(db_user)
    db.session.commit()

all_db_users = models.User.query.all()