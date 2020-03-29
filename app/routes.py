from app import app, db, models
import app.clients.spotify as sp
import app.clients.analysis as an
from datetime import date, timedelta
from flask import abort, jsonify, request
import json
import logging
import os
import requests
from threading import Thread

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
date_format = "%m/%d/%Y %I:%M:%S %p %Z"

graph_draw = an.Plotter()


def all_analysis(response_url, playlist_name):
    user_analysis(response_url, playlist_name)
    date_analysis(response_url, playlist_name)
    properties_analysis(response_url, playlist_name)


def user_analysis(response_url, playlist_name):
    logging.info("Responding to user analysis request")
    sp_client = sp.SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=app.config['SPOTIPY_CLIENT_ID'],
                                 SPOTIPY_CLIENT_SECRET=app.config['SPOTIPY_CLIENT_SECRET'])
    sp_client.connect()
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    if len(month_tracks) == 0:
        no_data_response = json.dumps({
            "response_type": "in_channel",
            "text": f"`{playlist_name}` is currently empty! Add songs to see user data."
        })
        requests.post(response_url, data=no_data_response)
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

        text_response_data = json.dumps({
            "response_type": "in_channel",
            "text": f"Thanks to all the contributors for this month! {slack_usernames}"
        })
        requests.post(response_url, data=text_response_data)

        image_data = json.dumps({
            "response_type": "in_channel",
            "text": f"User plot is here!",
            "blocks": [
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
        })
        requests.post(response_url, data=image_data)
    logging.info("Request completed")


def date_analysis(response_url, playlist_name, today_pad=True):
    logging.info("Responding to data analysis request")
    sp_client = sp.SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=app.config['SPOTIPY_CLIENT_ID'],
                                 SPOTIPY_CLIENT_SECRET=app.config['SPOTIPY_CLIENT_SECRET'])
    sp_client.connect()
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    if len(month_tracks) == 0:
        no_data_response = json.dumps({
            "response_type": "in_channel",
            "text": f"`{playlist_name}` is currently empty! Add songs to see date data."
        })
        requests.post(response_url, data=no_data_response)
    else:
        day_count = an.track_count_per_day(
            month_tracks, pad_to_today=today_pad)
        day_freq_message = ""
        for day, count in day_count.items():
            day_freq_message += f"{day}: {count} songs \n"
        day_graph_title = f"{playlist_name} Tracks Added by Day"
        image_url = graph_draw.line_graph(day_count.keys(), day_count.values(
        ), title=day_graph_title, xaxis='Day of month', yaxis='Songs Added')

        text_response_data = json.dumps({
            "response_type": "in_channel",
            "text": f"Here are the songs that have been added per day for `{playlist_name}`"
        })
        requests.post(response_url, data=text_response_data)

        image_data = json.dumps({
            "response_type": "in_channel",
            "text": f"Date plot is here!",
            "blocks": [
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
        })

        response = requests.post(response_url, data=image_data)
    logging.info("Request completed")


def properties_analysis(response_url, playlist_name):
    logging.info("Responding to properties analysis request")
    sp_client = sp.SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=app.config['SPOTIPY_CLIENT_ID'],
                                 SPOTIPY_CLIENT_SECRET=app.config['SPOTIPY_CLIENT_SECRET'])
    sp_client.connect()
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    if len(month_tracks) == 0:
        no_data_response = json.dumps({
            "response_type": "in_channel",
            "text": f"`{playlist_name}` is currently empty! Add songs to see audio properties data."
        })
        requests.post(response_url, data=no_data_response)
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

        text_response_data = json.dumps({
            "response_type": "in_channel",
            "text": f"Here are the audio characteristics of `{playlist_name}`"
        })
        requests.post(response_url, data=text_response_data)

        image_data = json.dumps({
            "response_type": "in_channel",
            "text": f"Properties plot is here!",
            "blocks": [
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
        })
        requests.post(response_url, data=image_data)
    logging.info("Request completed")


def set_playlist_names(request):
    test = False
    if "test" in request.form['text']:
        valid_user(request)
        test = True

    request_info = request.form['text']
    request_info = request_info.replace(' test', '')

    current_month_name = date.today().strftime("%B")
    last_month_name = (date.today() - (timedelta(weeks=5))).strftime("%B")
    playlist_prefix = "TEST " if test else "Song Roulette: "
    channel_name = "#sr-test" if test else "#dank-tunes"
    current_playlist_link = None

    old_playlist_name = f"{playlist_prefix}{last_month_name}"
    all_playlist_name = f"{playlist_prefix}All Songs"
    new_playlist_name = f"{playlist_prefix}{current_month_name}"

    return (request_info, old_playlist_name, all_playlist_name, new_playlist_name)


def valid_request(request):
    valid_token = request.form['token'] == app.config['SLACK_REQUEST_TOKEN']
    team_id = request.form['team_id'] == app.config['SLACK_TEAM_ID']
    if not (valid_token and team_id):
        abort(400)


def valid_user(request):
    if not request.form['user_id'] == app.config['SLACK_BOT_ADMIN']:
        return jsonify(
            text=f"Sorry, only <@{app.config['SLACK_BOT_ADMIN']}> has access to this command right now."
        )


@app.route('/refresh', methods=['POST'])
def refresh():
    logging.info(f"Received a refresh request from {request.form['user_id']}")
    valid_request(request)
    valid_user(request)
    request_type, old_playlist_name, all_playlist_name, new_playlist_name = set_playlist_names(
        request)
    sp_client = sp.SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=app.config['SPOTIPY_CLIENT_ID'],
                                 SPOTIPY_CLIENT_SECRET=app.config['SPOTIPY_CLIENT_SECRET'])
    sp_client.connect()
    return jsonify(
        response_type="in_channel",
        text="You made a refresh request!"
    )


@app.route('/analysis', methods=['POST'])
def analysis():
    logging.info(
        f"Received an analysis request from {request.form['user_id']}")
    valid_request(request)
    valid_user(request)
    analysis_type, old_playlist_name, all_playlist_name, new_playlist_name = set_playlist_names(
        request)

    if analysis_type == "users":
        worker_thread = Thread(target=user_analysis, args=(
            request.form['response_url'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "dates":
        worker_thread = Thread(target=date_analysis, args=(
            request.form['response_url'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "properties":
        worker_thread = Thread(target=properties_analysis, args=(
            request.form['response_url'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "all":
        worker_thread = Thread(target=all_analysis, args=(
            request.form['response_url'], new_playlist_name, ))
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
