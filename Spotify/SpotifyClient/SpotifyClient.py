import datetime
#import json
import os
import spotipy
import spotipy.util as util

class SpotifyClient():
    """Class for handling all Spotify API requests"""

    def __init__(self):
        """Initializes an object with all necessary items to create a Spotify Client"""
        self.client = None
        self.client_id = os.environ['SPOTIPY_CLIENT_ID']
        self.client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
        self.fields_filter = 'items(added_at,added_by,track(name,popularity,uri))'
        self.redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
        self.scope = "playlist-read-collaborative playlist-read-private playlist-modify-private playlist-modify-public"
        self.sr_analysis = True
        self.user_id = None
        self.username = None
        # if self.user_id == None or self.username == None:
        #     print("Check user ID and username in SpotifyClient!")
        #     exit()

    def connect(self):
        """Authentication for Spotify Client"""
        token = util.prompt_for_user_token(self.username, self.scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        self.client = spotipy.Spotify(auth=token) if token else None

    def get_audio_features(self, songs):
        """Returns audio features given a list of songs. Audio features call does not support offsetting, so list slicing is required."""
        return self.max_out_with_slice(self.client.audio_features, songs)

    #TODO: Add year confirmation to this method to avoid multiple months being returned
    def get_month_tracks(self, playlist_name, month, fields=None):
        """Returns the filtered track information of a given playlist name for tracks added in a specific month"""
        if type(month) is str:
            print("Please provide month as an integer")
            exit()
        if "added_at" not in fields:
            print("Please include added_at filter in fields")
            exit()
        filtered_tracks = []
        tracks = self.get_playlist_tracks(playlist_name, fields=fields)
        for track in tracks:
            if datetime.datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ').month - int(self.sr_analysis) == month:
                filtered_tracks.append(track)
        return filtered_tracks

    def get_playlist_id(self, playlist_name):
        """Returns a playlist ID for a given playlist name"""
        pid = -1
        all_playlists = self.client.current_user_playlists()
        for playlist in all_playlists['items']:
            if playlist['name'] == playlist_name:
                pid = playlist['id']
        if pid == -1:
            print("Playlist with name '%s' not found!" % playlist_name)
            #self.client.user_create_playlist(self.user_id, playlist_name)
            exit()
        return pid

    def get_playlist_tracks(self, playlist_name, fields=None):
        """Returns the filtered track information of a given playlist name"""
        fields = self.fields_filter if fields is None else fields
        pid = self.get_playlist_id(playlist_name)
        return self.max_out_with_offset(self.client.user_playlist_tracks, user=self.user_id, playlist_id=pid, fields=fields)

    def get_playlist_url(self, playlist_name):
        """Returns a playlist URL for a given playlist name"""
        playlist = self.client.user_playlist(self.user_id, self.get_playlist_id(playlist_name))
        return playlist['external_urls']['spotify']

    def max_out_with_slice(self, method_name, tracks, **kwargs):
        """Makes multiple requests when information is needed for >100 tracks for API endpoints that don't support offset"""
        counter = 0
        track_count = 100
        all_items = []
        while track_count == 100:
            end_slice = 100*(counter+1) if len(tracks) > 100*(counter + 1) else len(tracks)
            items = method_name(tracks=tracks[100*counter:end_slice], **kwargs)
            all_items += items
            track_count = end_slice - 100*counter
            counter += 1
        return all_items   

    def max_out_with_offset(self, method_name, **kwargs):
        """Makes multiple requests when information is needed for >100 tracks for API endpoints that support offset"""
        counter = 0
        track_count = 100
        all_items = []
        while track_count == 100:
            items = method_name(**kwargs, offset=100*counter)
            all_items += items['items']
            track_count = len(items['items'])
            counter += 1
        return all_items

    def move_tracks(self, from_playlist, to_playlist):
        """Move all tracks from one playlist to another"""
        from_id = self.get_playlist_id(from_playlist)
        to_id = self.get_playlist_id(to_playlist)
        tracks = self.get_playlist_tracks(from_playlist)
        tracks_to_move = [track['track']['uri'] for track in tracks]
        self.max_out_with_slice(self.client.user_playlist_add_tracks, tracks_to_move, user=self.user_id, playlist_id=to_id)
        self.max_out_with_slice(self.client.user_playlist_remove_all_occurrences_of_tracks, tracks_to_move, user=self.user_id, playlist_id=from_id)

    def rename_playlist(self, old_playlist_name, new_playlist_name):
        """Renames a playlist given old and new playlists"""
        self.client.user_playlist_change_details(self.user_id, self.get_playlist_id(old_playlist_name), new_playlist_name)

    def set_fields(self, fields):
        """Set the fields parameter used when making REST requests"""
        self.fields_filter = fields

if __name__ == "__main__":
    my_client = SpotifyClient()
    my_client.connect()
    my_client.fields_filter = None
    pl_tracks = my_client.get_playlist_tracks("Tabletops", fields='items(track(name,popularity,uri))')
    track_uris = []
    for track in pl_tracks:
        track_uris.append(track['track']['uri'])
    print(len(my_client.get_audio_features(track_uris)))
    exit()