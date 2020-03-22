# Script for monthly refresh
import analysis.client as AnalysisClient
import argparse
import datetime
from datetime import date, timedelta
from database.client.DatabaseClient import DatabaseClient
import json
from messaging.client import SlackClient
from spotify.client import SpotifyClient

def analysis(old_playlist_name, month_tracks):
    print("Running analysis...")
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
    user_graph_title = f"{old_playlist_name} Tracks Added per User"
    graph_draw.bar_graph(user_count_by_name.keys(), user_count_by_name.values(), title=user_graph_title, xaxis='User', yaxis='Songs Added')
    db_client.file_write(user_count, f"{old_playlist_name} data".replace(" ", "_").replace(":", "_"))

    day_count = AnalysisClient.track_count_per_day(month_tracks, pad_to_month_end=True)
    day_graph_title = f"{old_playlist_name} Tracks Added by Day"
    graph_draw.line_graph(day_count.keys(), day_count.values(), title=day_graph_title, xaxis='Day of month', yaxis='Songs Added')
    db_client.file_write(day_count)

    track_uris = sp_client.filter_tracks(month_tracks, 'uri')
    audio_features = sp_client.get_audio_features(track_uris)
    avg_audio_features = AnalysisClient.avg_audio_features(audio_features)
    features_graph_title = f"{old_playlist_name} Audio Features"
    graph_draw.radar_graph(avg_audio_features, title=features_graph_title)
    db_client.file_write(avg_audio_features)

    graph_titles = {'user': user_graph_title, 
                    'day': day_graph_title,
                    'features': features_graph_title}

    return (graph_titles, slack_usernames)

def connect(*args):
    print("Connecting clients...")
    for client in args:
        client.connect()

def parse_args():
    parser = argparse.ArgumentParser(description='Refresh monthly Spotify Playlist.')
    parser.add_argument('--test', help='Perform a test run of the refresh script', action='store_true')
    parser.add_argument('--live', help='Perform a live run of the refresh script. Specified day must match current day.', type=int)
    parser.add_argument('--reset-test', help='Reset the testing playlists', action='store_true')
    return parser.parse_args()

def main(args):
    """Refreshes playlist and performs all optional analysis"""
    test = args.test or args.reset_test
    live_run_day = args.live
    day_of_month = date.today().day

    current_month_name = date.today().strftime("%B")
    last_month_name = (date.today() - (timedelta(weeks=5) if test else timedelta(live_run_day))).strftime("%B")
    playlist_prefix = "TEST " if test else "Song Roulette: "
    channel_name = "#sr-test" if test else "#dank-tunes"
    current_playlist_link = None

    old_playlist_name = f"{playlist_prefix}{last_month_name}"
    all_playlist_name = f"{playlist_prefix}All Songs"
    new_playlist_name = f"{playlist_prefix}{current_month_name}"

    if args.reset_test:
        reset_test_playlist(old_playlist_name, new_playlist_name, all_playlist_name)
    elif day_of_month == (day_of_month if test else live_run_day):
        month_tracks = sp_client.get_playlist_tracks(old_playlist_name)
        db_client.file_write(month_tracks, f"{old_playlist_name} tracks".replace(" ", "_").replace(":", "_"))
        graph_titles, slack_usernames = analysis(old_playlist_name, month_tracks)
        
        reset_playlist(test, old_playlist_name, new_playlist_name, all_playlist_name)
        current_playlist_link = sp_client.get_playlist_url(new_playlist_name)

        message_slack(channel_name, new_playlist_name, current_playlist_link, slack_usernames, **graph_titles)
        print("This was a test run. Check test playlists and channel.") if test else print("This was a LIVE run.")
    else:
        print(f"Please enter the current day ({day_of_month}) if you would like to refresh the monthly playlist. You entered {live_run_day}.")

def message_slack(channel_name, new_playlist_name, current_playlist_link, slack_usernames, **kwargs):
    print("Messaging slack...")
    sl_client.set_channel(channel_name)
    sl_client.post_message(f"{new_playlist_name} is now ready! Add songs here: {current_playlist_link}")
    sl_client.post_message(f"Thanks to everyone who contributed last month! {slack_usernames}")
    sl_client.post_file(f"images/{kwargs.get('user')}.png".replace(" ", "_").replace(":", "_"), message="Here's how many songs everyone added.")
    sl_client.post_file(f"images/{kwargs.get('features')}.png".replace(" ", "_").replace(":", "_"), message="Here's the playlist features for last month.")
    sl_client.post_file(f"images/{kwargs.get('day')}.png".replace(" ", "_").replace(":", "_"), message="Here's how often songs were added throughout the month.")

def reset_playlist(test, old_playlist_name, new_playlist_name, all_playlist_name):
    run_type = 'TEST' if test else 'LIVE'
    if input(f"You've specified a {run_type} run. {old_playlist_name} will be moved to {all_playlist_name}. Enter Y to continue: ") != 'Y':
        print("Exiting...")
        exit()
    sp_client.move_tracks(old_playlist_name, all_playlist_name)
    sp_client.rename_playlist(old_playlist_name, new_playlist_name)

def reset_test_playlist(old_playlist_name, new_playlist_name, all_playlist_name):
    print("Resetting test playlist...")
    sp_client.move_tracks(all_playlist_name, new_playlist_name)
    sp_client.rename_playlist(new_playlist_name, old_playlist_name)
    print(f"Songs from {all_playlist_name} were moved back to {old_playlist_name}")

if __name__ == "__main__":
    cli_args = parse_args()
    with open('secrets.json', 'r') as json_secret:
        secret_info = json.load(json_secret)
    db_client = DatabaseClient(DATABASE_URL=secret_info['DATABASE_URL'])
    sl_client = SlackClient(SLACK_OAUTH_TOKEN=secret_info['SLACK_OAUTH_TOKEN'])
    sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt', SPOTIPY_CLIENT_ID=secret_info['SPOTIPY_CLIENT_ID'], 
                              SPOTIPY_CLIENT_SECRET=secret_info['SPOTIPY_CLIENT_SECRET'], SPOTIPY_REDIRECT_URI=secret_info['SPOTIPY_REDIRECT_URI'])
    connect(db_client, sp_client, sl_client)
    main(cli_args)
    exit()