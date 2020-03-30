import sys
sys.path.append('..')

from slackapp import date_format, db, models
import json
import sqlalchemy

def first_insert(user_info):
    return "Run in dev and prod"
    for user in user_info:
        db_user = models.User(spotify_id=user, slack_id=user_info[user]['slack_id'], display_name=user_info[user]['name'])
        db.session.add(db_user)
        db.session.commit()

    all_db_users = models.User.query.all()

def second_insert(user_info):
    return "Run in dev and prod"
    for user in user_info:
        admin_bool = True if user_info[user]["is_admin"] == "True" else False
        dev_bool = True if user_info[user]["dev_access"] == "True" else False
        prod_bool = True if user_info[user]["prod_access"] == "True" else False
        db_user = models.User.query.filter_by(spotify_id=user).update(dict(is_admin=admin_bool, dev_access=dev_bool, prod_access=prod_bool))
        db.session.commit()

def third_insert(user_info):
    for user in user_info:
        if "None" in user:
            admin_bool = True if user_info[user]["is_admin"] == "True" else False
            dev_bool = True if user_info[user]["dev_access"] == "True" else False
            prod_bool = True if user_info[user]["prod_access"] == "True" else False            
            db_user = models.User(spotify_id=sqlalchemy.null(), slack_id=user_info[user]['slack_id'], display_name=user_info[user]['name'], is_admin=admin_bool, dev_access=dev_bool, prod_access=prod_bool)
            db.session.add(db_user)
            db.session.commit()

if __name__ == "__main__":
    with open('../users.json', 'r') as json_file:
        user_info = json.load(json_file)
    third_insert(user_info)