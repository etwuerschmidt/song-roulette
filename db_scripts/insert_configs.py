from datetime import datetime, timedelta
import sys
sys.path.append('..')

from slackapp import date_format, db, models

def first_insert():
    insert_time = datetime.utcnow() - timedelta(weeks=5)
    last_refresh = models.Config('LAST_PLAYLIST_REFRESH_TIME', insert_time.strftime(date_format), 'The last time that the playlist was refreshed through a Slack call.')
    last_slash_call = models.Config('LAST_SLASH_COMMAND_TIME', insert_time.strftime(date_format), 'The last time a Slack slash command was called.')
    db.session.add(last_refresh)    
    db.session.add(last_slash_call)
    db.session.commit()

if __name__ == "__main__":
    first_insert()