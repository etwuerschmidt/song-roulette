import datetime
from datetime import date
import json
import os
import spotipy
import spotipy.util as util

class SpotifyClient():

	def __init__(self):
		'''Initializes an object with all necessary items to create a Spotify Client'''
		self.client = None
		self.client_id = os.environ['SPOTIPY_CLIENT_ID']
		self.client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
		self.fields_filter = None
		self.redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
		self.scope = 'playlist-read-collaborative playlist-read-private playlist-modify-private playlist-modify-public'
		self.user_id = None
		self.username = None
		if self.user_id == None or self.username == None:
			print("Check user ID and username in SpotifyClient!")
			exit()

	def connect(self):
		'''Authentication for Spotify Client'''
		token = util.prompt_for_user_token(self.username, 
			self.scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
		self.client = spotipy.Spotify(auth=token) if token else None

	def get_playlist_id(self, playlist_name):
		'''Returns a playlist ID for a given playlist name'''
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

	def get_playlist_url(self, playlist_name):
		'''Returns a playlist URL for a given playlist name'''
		playlist = self.client.user_playlist(self.user_id, self.get_playlist_id(playlist_name))
		return playlist['external_urls']['spotify']

	def get_current_tracks(self, playlist_name):
		'''Returns the filtered track information of a given playlist name'''
		pid = self.get_playlist_id(playlist_name)
		counter = 0
		track_count = 100
		self.set_fields('items(added_at,added_by.id,track(name,popularity,uri))')
		all_tracks = []
		while track_count == 100:
			tracks = self.client.user_playlist_tracks(self.user_id, pid, fields=self.fields_filter, offset=100*counter)
			all_tracks += tracks['items']
			track_count = len(tracks['items'])
			counter+=1
		return all_tracks

	#TODO: Add year confirmation to this method to avoid multiple months being returned
	def get_month_tracks(self, playlist_name, month):
		'''Returns the filtered track information of a given playlist name for tracks added in a specific month'''
		if type(month) is str:
			print("Please provide month as an integer")
			exit()
		pid = self.get_playlist_id(playlist_name)
		counter = 0
		track_count = 100
		self.set_fields('items(added_at,track(name,popularity,uri))')
		tracks = self.client.user_playlist_tracks(self.user_id, self.get_playlist_id(playlist_name), fields=self.fields_filter)
		filtered_tracks = []
		while track_count == 100:
			tracks = self.client.user_playlist_tracks(self.user_id, pid, fields=self.fields_filter, offset=100*counter)
			for track in tracks['items']:
				if datetime.datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ').month == month:
					filtered_tracks.append(track)
			track_count = len(tracks['items'])
			counter+=1
		return filtered_tracks
		
	def move_tracks(self, from_playlist, to_playlist):
		'''Move all tracks from one playlist to another'''
		from_id = self.get_playlist_id(from_playlist)
		to_id = self.get_playlist_id(to_playlist)
		tracks_to_move = []
		tracks = self.client.user_playlist_tracks(self.user_id, playlist_id=from_id)
		for track in tracks['items']:
			tracks_to_move.append(track['track']['uri'])
		self.client.user_playlist_add_tracks(self.user_id, to_id, tracks_to_move)
		self.client.user_playlist_remove_all_occurrences_of_tracks(self.user_id, from_id, tracks_to_move)

	def rename_playlist(self, old_playlist_name, new_playlist_name):
		'''Renames a playlist given old and new playlists'''
		self.client.user_playlist_change_details(self.user_id, self.get_playlist_id(old_playlist_name), new_playlist_name)

	def set_fields(self, fields):
		'''Set the fields parameter used when making REST requests'''
		self.fields_filter = fields

	def track_count_per_user(self, playlist_name):
		'''Returns the amount of songs per user that were added to a playlist'''
	    pid = self.client.get_playlist_id(playlist_name)
	    song_counter = {}
	    tracks = spotify_client.user_playlist_tracks(self.user_id, playlist_id=retrieved_id)
	    for track in tracks['items']:
	        if track['added_by']['id'] in song_counter:
	            song_counter[track['added_by']['id']]+=1
	        else:
	            song_counter[track['added_by']['id']]=1
	    return song_counter

if __name__ == "__main__":
	my_client = SpotifyClient()
	my_client.connect()
	tracks = my_client.get_month_tracks("Song Roulette: All Songs", 1)
	print(tracks)
	exit()