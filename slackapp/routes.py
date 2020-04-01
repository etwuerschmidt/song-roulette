from slackapp import app, date_format, db, models
import slackapp.clients.spotify as sp
import slackapp.clients.analysis as an
import slackapp.clients.messaging as mes
from datetime import date, datetime, timedelta
from flask import abort, jsonify, request, Response
import json
import os
import requests
from threading import Thread
import time

graph_draw = an.Plotter()


def connect_clients(channel_id):
    sp_client = sp.SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=app.config['SPOTIPY_CLIENT_ID'],
                                 SPOTIPY_CLIENT_SECRET=app.config['SPOTIPY_CLIENT_SECRET'])
    sp_client.connect()
    sl_client = mes.SlackClient()
    sl_client.connect()
    sl_client.set_channel(channel_id)
    return (sp_client, sl_client)


def all_analysis(channel_id, playlist_name, pad_to_today, pad_to_month_end):
    app.logger.info(f"Beginning to run all analysis")
    user_analysis(channel_id, playlist_name)
    date_analysis(channel_id, playlist_name, pad_to_today, pad_to_month_end)
    properties_analysis(channel_id, playlist_name)


def user_analysis(channel_id, playlist_name):
    app.logger.info("Responding to user analysis request")
    sp_client, sl_client = connect_clients(channel_id)
    try:
        month_tracks = sp_client.get_playlist_tracks(playlist_name)
    except:
        timestamp = datetime.utcnow().strftime(date_format)
        sl_client.post_message(
            mes.slack_error_msg.format(timestamp, sl_client.admin))
        return
    if len(month_tracks) == 0:
        sl_client.post_message(
            f"`{playlist_name}` is currently empty! Add songs to see user data.")
    else:
        user_count = an.track_count_per_user(month_tracks)
        user_count_by_name = {}
        slack_usernames = ""
        for user, count in user_count.items():
            db_user = models.User.query.filter_by(spotify_id=user).first()
            if not db_user:
                user_count_by_name[user] = count
                slack_usernames += f"User {user} "
            else:
                user_count_by_name[db_user.display_name] = count
                slack_usernames += f"<{db_user.slack_id}> "
        user_graph_title = f"{playlist_name} Tracks Added per User"
        image_url = graph_draw.bar_graph(user_count_by_name.keys(), user_count_by_name.values(
        ), title=user_graph_title, xaxis='User', yaxis='Songs Added')

        sl_client.post_message(
            f"Thanks to all the contributors! {slack_usernames}")

        image_block = [
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "User frequency plot"
                },
                "image_url": image_url[:-1] + '.png',
                "alt_text": "This month's user data"
            }
        ]
        sl_client.post_block(image_block)
    last_slack_call_config = models.Config.query.filter_by(
        config_name="LAST_SLASH_COMMAND_TIME").first()
    last_slack_call_config.value = datetime.utcnow().strftime(date_format)
    db.session.commit()
    app.logger.info("Request completed")


def date_analysis(channel_id, playlist_name, pad_to_today, pad_to_month_end):
    app.logger.info("Responding to data analysis request")
    sp_client, sl_client = connect_clients(channel_id)
    try:
        month_tracks = sp_client.get_playlist_tracks(playlist_name)
    except:
        timestamp = datetime.utcnow().strftime(date_format)
        sl_client.post_message(
            mes.slack_error_msg.format(timestamp, sl_client.admin))
        return
    if len(month_tracks) == 0:
        sl_client.post_message(
            f"`{playlist_name}` is currently empty! Add songs to see date data.")
    else:
        day_count = an.track_count_per_day(
            month_tracks, pad_to_today=pad_to_today, pad_to_month_end=pad_to_month_end)
        day_freq_message = ""
        for day, count in day_count.items():
            day_freq_message += f"{day}: {count} songs \n"
        day_graph_title = f"{playlist_name} Tracks Added by Day"
        image_url = graph_draw.line_graph(day_count.keys(), day_count.values(
        ), title=day_graph_title, xaxis='Day of month', yaxis='Songs Added')

        sl_client.post_message(
            f"Here are the songs that have been added per day for `{playlist_name}`")

        image_blocks = [
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "Date frequency plot"
                },
                "image_url": image_url[:-1] + '.png',
                "alt_text": "This month's date data"
            }
        ]

        sl_client.post_block(image_blocks)
    last_slack_call_config = models.Config.query.filter_by(
        config_name="LAST_SLASH_COMMAND_TIME").first()
    last_slack_call_config.value = datetime.utcnow().strftime(date_format)
    db.session.commit()
    app.logger.info("Request completed")


def properties_analysis(channel_id, playlist_name):
    app.logger.info("Responding to properties analysis request")
    sp_client, sl_client = connect_clients(channel_id)
    try:
        month_tracks = sp_client.get_playlist_tracks(playlist_name)
    except:
        timestamp = datetime.utcnow().strftime(date_format)
        sl_client.post_message(
            mes.slack_error_msg.format(timestamp, sl_client.admin))
        return
    if len(month_tracks) == 0:
        sl_client.post_message(
            f"`{playlist_name}` is currently empty! Add songs to see audio properties data.")
    else:
        track_uris = sp_client.filter_tracks(month_tracks, 'uri')
        audio_features = sp_client.get_audio_features(track_uris)
        avg_audio_features = an.avg_audio_features(
            audio_features)
        features_message = ""
        for feature, quan in avg_audio_features.items():
            features_message += f"{feature}: {quan} \n"
        features_graph_title = f"{playlist_name} Audio Features"
        image_url = graph_draw.radar_graph(
            avg_audio_features, title=features_graph_title)

        sl_client.post_message(
            f"Here are the audio characteristics of `{playlist_name}`")

        image_block = [
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "Audio analysis plot"
                },
                "image_url": image_url[:-1] + '.png',
                "alt_text": "This month's properties data"
            }
        ]
        sl_client.post_block(image_block)
    last_slack_call_config = models.Config.query.filter_by(
        config_name="LAST_SLASH_COMMAND_TIME").first()
    last_slack_call_config.value = datetime.utcnow().strftime(date_format)
    db.session.commit()
    app.logger.info("Request completed")


def refresh_playlist(channel_id, old_playlist_name, new_playlist_name, all_playlist_name):
    app.logger.info("Responding to refresh request")
    sp_client, sl_client = connect_clients(channel_id)
    last_refresh_config = models.Config.query.filter_by(
        config_name="LAST_PLAYLIST_REFRESH_TIME").first()
    if datetime.strptime(last_refresh_config.value, date_format).month == datetime.utcnow().month:
        app.logger.error(
            f"Playlist refresh for this month already occured at {last_refresh_config.value}. No refresh occuring.")
        sl_client.post_message(
            f"Sorry, but the playlist has already been refreshed this month, at {last_refresh_config.value} UTC")
        app.logger.info("Request aborting")
    else:
        all_analysis(channel_id, old_playlist_name, False, True)
        sp_client.move_tracks(old_playlist_name, all_playlist_name)
        sp_client.rename_playlist(old_playlist_name, new_playlist_name)
        current_playlist_link = sp_client.get_playlist_url(new_playlist_name)
        last_refresh_config.value = datetime.utcnow().strftime(date_format)
        last_slack_call_config = models.Config.query.filter_by(
            config_name="LAST_SLASH_COMMAND_TIME").first()
        last_slack_call_config.value = datetime.utcnow().strftime(date_format)
        db.session.commit()
        sl_client.post_message(
            f"`{new_playlist_name}` is now ready! Add songs here: {current_playlist_link}")
        app.logger.info("Request completed")


def set_playlist_names(request):
    test = False
    if "test" in request.form['text']:
        valid_user(request)
        test = True

    request_info = request.form['text']
    request_info = request_info.replace(' test', '')

    current_month_name = date.today().strftime("%B")
    last_month_name = (date.today() - (timedelta(weeks=3))).strftime("%B")
    playlist_prefix = "TEST " if test else "Song Roulette: "
    channel_name = "#sr-test" if test else "#dank-tunes"
    current_playlist_link = None

    old_playlist_name = f"{playlist_prefix}{last_month_name}"
    all_playlist_name = f"{playlist_prefix}All Songs"
    new_playlist_name = f"{playlist_prefix}{current_month_name}"

    return (request_info, old_playlist_name, all_playlist_name, new_playlist_name)


def valid_request(request):
    app.logger.info(f"Validating request")
    valid_token = request.form['token'] == app.config['SLACK_REQUEST_TOKEN']
    team_id = request.form['team_id'] == app.config['SLACK_TEAM_ID']
    if not (valid_token and team_id):
        app.logger.error(
            f"Invalid request with token {request.form['token']} and team {request.form['team_id']}")
        abort(400)


def valid_user(request, access_type='prod'):
    app.logger.info(f"Validating user has access to {access_type}")
    users = []
    if access_type == 'admin':
        users = models.User.query.filter_by(is_admin=True).all()
    elif access_type == 'dev':
        users = models.User.query.filter_by(dev_access=True).all()
    elif access_type == 'prod':
        users = models.User.query.filter_by(prod_access=True).all()
    else:
        timestamp = datetime.utcnow().strftime(date_format)
        app.logger.error(f"Invalid user type {access_type}")
        return jsonify(mes.slack_error_msg(timestamp))

    valid_user_ids = [user.slack_id for user in users]
    request_user = f"@{request.form['user_id']}"

    if not request_user in valid_user_ids:
        app.logger.error(
            f"User {request.form['user_id']} does not have {access_type} access")
        abort(
            Response(f"Sorry, looks like you don't have `{access_type}` access."))


def wake_up(response_url, response_text):
    app.logger.info("Responding to wake request")
    data = json.dumps({
        "response_type": "in_channel",
        "text": response_text
    })
    try:
        requests.post(response_url, data=data)
    except Exception as e:
        app.logger.exception(e)


@app.route('/refresh', methods=['POST'])
def refresh():
    app.logger.info(
        f"Received a refresh request from {request.form['user_id']}")
    valid_request(request)
    valid_user(request)
    request_type, old_playlist_name, all_playlist_name, new_playlist_name = set_playlist_names(
        request)
    worker_thread = Thread(target=refresh_playlist, args=(
        request.form['channel_id'], old_playlist_name, new_playlist_name, all_playlist_name, ))
    worker_thread.start()
    return jsonify(
        response_type="in_channel",
        text=f"Processing your refresh request for `{old_playlist_name}` now - this may take a little bit"
    )


@app.route('/analysis', methods=['POST'])
def analysis():
    app.logger.info(
        f"Received an analysis request from {request.form['user_id']}")
    valid_request(request)
    valid_user(request)
    analysis_type, old_playlist_name, all_playlist_name, new_playlist_name = set_playlist_names(
        request)

    if analysis_type == "users":
        worker_thread = Thread(target=user_analysis, args=(
            request.form['channel_id'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "dates":
        worker_thread = Thread(target=date_analysis, args=(
            request.form['channel_id'], new_playlist_name, True, False, ))
        worker_thread.start()
    elif analysis_type == "properties":
        worker_thread = Thread(target=properties_analysis, args=(
            request.form['channel_id'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "all":
        worker_thread = Thread(target=all_analysis, args=(
            request.form['channel_id'], new_playlist_name, True, False))
        worker_thread.start()
    else:
        return jsonify(
            response_type="in_channel",
            text=f"`{analysis_type}` is not supported with `/analysis`. Please use `all`, `users`, `dates`, or `properties`"
        )

    return jsonify(
        response_type="in_channel",
        text=f"Processing your analysis request for `{analysis_type}` now - this may take a little bit"
    )


@app.route('/wake', methods=['POST'])
def wake():
    user_id = request.form.get('user_id', None)
    response_text = ''
    if user_id:
        app.logger.info(f"Received a wake request from {user_id}")
        valid_request(request)
        valid_user(request)
        response_text = f"<@{user_id}> I'm up! If you received a timeout error earlier that's to be expected. I'll be awake for the next 30 minutes."
    else:
        app.logger.info(
            f"Received a wake request with no user - this might be an external call to this endpoint")
        response_text = f"I'm up! I'll be awake for the next 30 minutes."
    worker_thread = Thread(target=wake_up, args=(
        request.form['response_url'], response_text,))
    worker_thread.start()

    return jsonify(
        response_type="in_channel",
        text="Processing your wake request now"
    )
