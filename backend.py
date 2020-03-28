import analysis.client as AnalysisClient
import argparse
import datetime
from datetime import date, timedelta
# from database.client import DatabaseClient
from flask import abort, g, Flask, jsonify, request
import json
# from messaging.client import SlackClient
import logging
import os
import requests
from spotify.client import SpotifyClient
from threading import Thread

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
date_format = "%m/%d/%Y %I:%M:%S %p %Z"


def connect_clients(*args):
    print("Connecting clients...")
    for client in args:
        client.connect()


sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=os.environ['SPOTIPY_CLIENT_ID'],
                          SPOTIPY_CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET'])
connect_clients(sp_client)
graph_draw = AnalysisClient.Plotter()
app = Flask(__name__)


def all_analysis(response_url, playlist_name):
    user_analysis(response_url, playlist_name)
    date_analysis(response_url, playlist_name)
    properties_analysis(response_url, playlist_name)


def user_analysis(response_url, playlist_name):
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    with open('users.json', 'r') as json_file:
        user_info = json.load(json_file)
    user_count = AnalysisClient.track_count_per_user(month_tracks)
    user_count_by_name = {}
    slack_usernames = ""
    for user, count in user_count.items():
        if user not in user_info:
            user_count_by_name[user] = count
            slack_usernames += f"User {user} "
        else:
            user_count_by_name[user_info[user]['name']] = count
            slack_usernames += f"<{user_info[user]['slack_id']}> "
    current_time = datetime.datetime.now().strftime(date_format).strip()
    user_graph_title = f"{playlist_name} Tracks Added per User - {current_time}"
    image_url = graph_draw.bar_graph(user_count_by_name.keys(), user_count_by_name.values(
    ), title=user_graph_title, xaxis='User', yaxis='Songs Added')

    logging.info("Responding to user analysis request")

    text_response_data = json.dumps({
        "response_type": "in_channel",
        "text": f"Thanks to all the contributors for this month! {slack_usernames}"
    })
    requests.post(response_url, data=text_response_data)

    image_data = json.dumps({
        "response_type": "in_channel",
        "text": f"Whoops! Looks like something went wrong with displaying the user data",
        "blocks": [
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "Date frequency plot"
                },
                "image_url": image_url[:-1] + '.png',
                "alt_text": "This month's user data"
            }
        ]
    })
    requests.post(response_url, data=image_data)
    logging.info("Request completed")


def date_analysis(response_url, playlist_name, today_pad=True):
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    day_count = AnalysisClient.track_count_per_day(
        month_tracks, pad_to_today=today_pad)
    day_freq_message = ""
    for day, count in day_count.items():
        day_freq_message += f"{day}: {count} songs \n"
    current_time = datetime.datetime.now().strftime(date_format).strip()
    day_graph_title = f"{playlist_name} Tracks Added by Day - {current_time}"
    image_url = graph_draw.line_graph(day_count.keys(), day_count.values(
    ), title=day_graph_title, xaxis='Day of month', yaxis='Songs Added')

    logging.info("Responding to data analysis request")

    text_response_data = json.dumps({
        "response_type": "in_channel",
        "text": f"Here are the songs that have been added per day for `{playlist_name}`"
    })
    requests.post(response_url, data=text_response_data)

    image_data = json.dumps({
        "response_type": "in_channel",
        "text": f"Whoops! Looks like something went wrong with displaying the date data",
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
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    track_uris = sp_client.filter_tracks(month_tracks, 'uri')
    audio_features = sp_client.get_audio_features(track_uris)
    avg_audio_features = AnalysisClient.avg_audio_features(audio_features)
    features_message = ""
    for feature, quan in avg_audio_features.items():
        features_message += f"{feature}: {quan} \n"
    current_time = datetime.datetime.now().strftime(date_format).strip()
    features_graph_title = f"{playlist_name} Audio Features - {current_time}"
    image_url = graph_draw.radar_graph(
        avg_audio_features, title=features_graph_title)

    logging.info("Responding to properties analysis request")

    text_response_data = json.dumps({
        "response_type": "in_channel",
        "text": f"Here are the audio characteristics of `{playlist_name}`"
    })
    requests.post(response_url, data=text_response_data)

    image_data = json.dumps({
        "response_type": "in_channel",
        "text": f"Whoops! Looks like something went wrong with displaying the properties data",
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


def run_server():
    app.run()


def set_playlist_names(request):
    test = False
    if "test" in request.form['text'] and "/refresh" == request.form['command']:
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
    valid_token = request.form['token'] == os.environ['SLACK_REQUEST_TOKEN']
    team_id = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
    if not (valid_token and team_id):
        abort(400)


def valid_user(request):
    if not request.form['user_id'] == os.environ['SLACK_BOT_ADMIN']:
        return jsonify(
            text=f"Sorry, only <@{os.environ['SLACK_BOT_ADMIN']}> has access to this command right now."
        )


@app.route('/refresh', methods=['POST'])
def refresh():
    logging.info(f"Received a refresh request from {request.form['user_id']}")
    valid_request(request)
    valid_user(request)
    request_type, old_playlist_name, all_playlist_name, new_playlist_name = set_playlist_names(
        request)
    sp_client.refresh_access()
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
    sp_client.refresh_access()

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


if __name__ == "__main__":
    # db_client = DatabaseClient(DATABASE_URL=secret_info['DATABASE_URL'])
    # sl_client = SlackClient(SLACK_OAUTH_TOKEN=secret_info['SLACK_OAUTH_TOKEN'])
    run_server()
