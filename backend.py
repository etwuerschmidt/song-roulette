import analysis.client as AnalysisClient
import argparse
import datetime
from datetime import date, timedelta
# from database.client import DatabaseClient
from flask import abort, Flask, jsonify, request
import json
# from messaging.client import SlackClient
import requests
from spotify.client import SpotifyClient
from threading import Thread

app = Flask(__name__)

def connect_clients(*args):
    print("Connecting clients...")
    for client in args:
        client.connect()

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
    user_graph_title = f"{playlist_name} Tracks Added per User"
    graph_draw.bar_graph(user_count_by_name.keys(), user_count_by_name.values(), title=user_graph_title, xaxis='User', yaxis='Songs Added')

    data = {
        "response_type": "in_channel",
        "text": f"Here are all our contributors for {playlist_name}: {slack_usernames}"
    }
    requests.post(response_url, json=data)

def date_analysis(response_url, playlist_name):
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    day_count = AnalysisClient.track_count_per_day(month_tracks, pad_to_month_end=True)
    day_freq_message = ""
    for day, count in day_count.items():
        day_freq_message += f"{day}: {count} songs \n"
    day_graph_title = f"{playlist_name} Tracks Added by Day"
    graph_draw.line_graph(day_count.keys(), day_count.values(), title=day_graph_title, xaxis='Day of month', yaxis='Songs Added')

    data = {
        "response_type": "in_channel",
        "text": f"Here are the songs that have been added per day for {playlist_name}: \n {day_freq_message}"
    }
    requests.post(response_url, json=data)

def properties_analysis(response_url, playlist_name):
    month_tracks = sp_client.get_playlist_tracks(playlist_name)
    track_uris = sp_client.filter_tracks(month_tracks, 'uri')
    audio_features = sp_client.get_audio_features(track_uris)
    avg_audio_features = AnalysisClient.avg_audio_features(audio_features)
    features_message = ""
    for feature, quan in avg_audio_features.items():
        features_message += f"{feature}: {quan} \n"
    features_graph_title = f"{playlist_name} Audio Features"
    graph_draw.radar_graph(avg_audio_features, title=features_graph_title)
    
    data = {
        "response_type": "in_channel",
        "text": f"Here are the audio characteristics of {playlist_name}: \n {features_message}"
    }
    requests.post(response_url, json=data)

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
    valid_token = request.form['token'] == token
    team_id = request.form['team_id'] == team
    if not (valid_token and team_id):
        abort(400)

def valid_user(request):
    if not request.form['user_id'] == admin:
        return jsonify(
            text=f"Sorry, only <@{admin}> has access to this command right now."
        )

@app.route('/refresh', methods=['POST'])
def refresh():
    valid_request(request)
    valid_user(request)
    request_type, old_playlist_name, all_playlist_name, new_playlist_name = set_playlist_names(request)
    return jsonify(
        response_type="in_channel",
        text="You made a refresh request!"
    )

@app.route('/analysis', methods=['POST'])
def analysis():
    valid_request(request)
    valid_user(request)
    analysis_type, old_playlist_name, all_playlist_name, new_playlist_name = set_playlist_names(request)

    if analysis_type == "users":
        worker_thread = Thread(target=user_analysis, args=(request.form['response_url'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "dates":
        worker_thread = Thread(target=date_analysis, args=(request.form['response_url'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "properties":
        worker_thread = Thread(target=properties_analysis, args=(request.form['response_url'], new_playlist_name, ))
        worker_thread.start()
    elif analysis_type == "all":
        worker_thread = Thread(target=all_analysis, args=(request.form['response_url'], new_playlist_name, ))
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
    with open('secrets.json', 'r') as json_secret:
        secret_info = json.load(json_secret)    
    # db_client = DatabaseClient(DATABASE_URL=secret_info['DATABASE_URL'])
    # sl_client = SlackClient(SLACK_OAUTH_TOKEN=secret_info['SLACK_OAUTH_TOKEN'])
    sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=secret_info['SPOTIPY_CLIENT_ID'], 
                              SPOTIPY_CLIENT_SECRET=secret_info['SPOTIPY_CLIENT_SECRET'], SPOTIPY_REDIRECT_URI=secret_info['SPOTIPY_REDIRECT_URI'])
    connect_clients(sp_client)
    token = secret_info['SLACK_REQUEST_TOKEN']
    team = secret_info['SLACK_TEAM_ID']
    admin = secret_info['SLACK_BOT_ADMIN']
    graph_draw = AnalysisClient.Plotter(save=True)
    run_server()