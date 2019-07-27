import json
import os
import requests
import slack
import sys
import spotipy
import spotipy.util as util

def analysis(spotify_client):
    playlists = spotify_client.current_user_playlists()
    retrieved_id = 0
    song_counter = {}
    for playlist in playlists['items']:
        if playlist['name'] == 'Song Roulette: July':
            retrieved_id = playlist['id']
    print(retrieved_id)
    tracks = spotify_client.user_playlist_tracks(user_mapping['me']['id'], playlist_id=retrieved_id)
    for track in tracks['items']:
        if track['added_by']['id'] in song_counter:
            song_counter[track['added_by']['id']]+=1
        else:
            song_counter[track['added_by']['id']]=1
    print(song_counter)

def move_playlist(spotify_client):
    playlists = spotify_client.current_user_playlists()
    from_id = 0
    to_id = 0
    tracks_to_move = []
    for playlist in playlists['items']:
        if playlist['name'] == 'Song Roulette: July':
            from_id = playlist['id']
        elif playlist['name'] == 'Testing Some Stuff':
            to_id = playlist['id']
    tracks = spotify_client.user_playlist_tracks(user_mapping['me']['id'], playlist_id=from_id)
    for track in tracks['items']:
        tracks_to_move.append(track['track']['uri'])
    print(tracks_to_move)
    print(to_id)
    spotify_client.user_playlist_add_tracks(user_mapping['me']['id'], to_id, tracks_to_move)
    spotify_client.user_playlist_remove_all_occurrences_of_tracks(user_mapping['me']['id'], to_id, tracks_to_move)

if __name__ == "__main__":

    with open('users.json') as json_file:
        user_mapping = json.load(json_file)

    print(user_mapping)

    scope = 'playlist-read-collaborative playlist-read-private playlist-modify-private playlist-modify-public'

    token = util.prompt_for_user_token(user_mapping['me']['display_name'], scope, 
    client_id=os.environ['SPOTIPY_CLIENT_ID'], 
    client_secret=os.environ['SPOTIPY_CLIENT_SECRET'], 
    redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'])

    slack_client = slack.WebClient(token=os.environ['SLACK_OAUTH_TOKEN'])
    SLACK = False

    if SLACK:
        response = slack_client.chat_postMessage(
            channel='#dank-tunes',
            text="Hello world!")

        print(response['message'])

    if token:
        sp = spotipy.Spotify(auth=token)
        move_playlist(sp)
    else:
        print("Can't get token for", user_mapping['me']['display_name'])