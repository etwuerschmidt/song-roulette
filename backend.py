import analysis.client as AnalysisClient
import argparse
import datetime
from datetime import date, timedelta
from database.client.DatabaseClient import DatabaseClient
from flask import abort, Flask, jsonify, request
import json
from messaging.client import SlackClient
import requests
from spotify.client import SpotifyClient
from threading import Thread

app = Flask(__name__)

def connect_clients(*args):
    print("Connecting clients...")
    for client in args:
        client.connect()

# @app.teardown_request
# def close_clients(error=None):
#     g.db_client.close()
#     g.sl_client.close()
#     g.sp_client.close()

def user_analysis(response_url):
    month_tracks = sp_client.get_playlist_tracks("Song Roulette: March")
    with open('users.json', 'r') as json_file:
        user_info = json.load(json_file)
    graph_draw = AnalysisClient.Plotter(save=True)
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
    user_graph_title = f"Song Roulette: March Tracks Added per User"
    graph_draw.bar_graph(user_count_by_name.keys(), user_count_by_name.values(), title=user_graph_title, xaxis='User', yaxis='Songs Added')

    data = {
        "response_type": "in_channel",
        "text": f"Here are all our contributors! {slack_usernames}"
    }
    requests.post(response_url, json=data)

def run_server():
    app.run()

def valid_request(request):
    valid_token = request.form['token'] == "OniQDbwoJu7mTGTX8Ub7LeCm"
    team_id = request.form['team_id'] == "T8K6M2S2D"
    if not (valid_token and team_id):
        abort(400)

def valid_user(request):
    if not request.form['user_id'] == 'U8WRDEPRT':
        return jsonify(
            text=f"Sorry, only <@U8WRDEPRT> has access to this slash command right now."
        )

@app.route('/refresh', methods=['POST'])
def refresh():
    valid_request(request)
    valid_user(request)
    return jsonify(
        response_type="in_channel",
        text="You made a refresh request!"
    )

@app.route('/analysis', methods=['POST'])
def analysis():
    valid_request(request)
    valid_user(request)

    analysis_type = request.form['text']

    if analysis_type == "users":
        worker_thread = Thread(target=user_analysis, args=(request.form['response_url'], ))
        worker_thread.start()

    return jsonify(
        response_type="in_channel",
        text="Processing your analysis request for users now - this may take a little bit"
    )

if __name__ == "__main__":
    with open('secrets.json', 'r') as json_secret:
        secret_info = json.load(json_secret)    
    db_client = DatabaseClient(DATABASE_URL=secret_info['DATABASE_URL'])
    sl_client = SlackClient(SLACK_OAUTH_TOKEN=secret_info['SLACK_OAUTH_TOKEN'])
    sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=secret_info['SPOTIPY_CLIENT_ID'], 
                              SPOTIPY_CLIENT_SECRET=secret_info['SPOTIPY_CLIENT_SECRET'], SPOTIPY_REDIRECT_URI=secret_info['SPOTIPY_REDIRECT_URI'])
    connect_clients(db_client, sp_client, sl_client)
    run_server()