import json
import os
import spotipy
import spotipy.util as util

class SpotifyClient():

	def __init__(self):
		self.client = None
		self.client_id = os.environ['SPOTIPY_CLIENT_ID']
		self.client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
		self.redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
		self.scope = 'playlist-read-collaborative playlist-read-private playlist-modify-private playlist-modify-public'
		self.user_id = None
		self.username = None

	# Just storing this here from old driver
	# def analysis(spotify_client):
	#     playlists = spotify_client.current_user_playlists()
	#     retrieved_id = 0
	#     song_counter = {}
	#     for playlist in playlists['items']:
	#         if playlist['name'] == 'Song Roulette: July':
	#             retrieved_id = playlist['id']
	#     print(retrieved_id)
	#     tracks = spotify_client.user_playlist_tracks(user_mapping['me']['id'], playlist_id=retrieved_id)
	#     for track in tracks['items']:
	#         if track['added_by']['id'] in song_counter:
	#             song_counter[track['added_by']['id']]+=1
	#         else:
	#             song_counter[track['added_by']['id']]=1
	#     print(song_counter)	

	def connect(self):
		token = util.prompt_for_user_token(self.username, 
			self.scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
		self.client = spotipy.Spotify(auth=token) if token else None

	def get_playlist_id(self, playlist_name):
		playlist_id = -1
		all_playlists = self.client.current_user_playlists()
		for playlist in all_playlists['items']:
			if playlist['name'] == playlist_name:
				playlist_id = playlist['id']
		if playlist_id == -1:
			print("Playlist with name '%s' not found!" % playlist_name)
			#self.client.user_create_playlist(self.user_id, playlist_name)
			exit()
		return playlist_id

	def get_playlist_url(self, playlist_name):
		playlist = self.client.user_playlist(self.user_id, self.get_playlist_id(playlist_name))
		return playlist['external_urls']['spotify']
		
	def move_tracks(self, from_playlist, to_playlist):
		from_id = self.get_playlist_id(from_playlist)
		to_id = self.get_playlist_id(to_playlist)
		tracks_to_move = []
		tracks = self.client.user_playlist_tracks(self.user_id, playlist_id=from_id)
		for track in tracks['items']:
			tracks_to_move.append(track['track']['uri'])
		self.client.user_playlist_add_tracks(self.user_id, to_id, tracks_to_move)
		self.client.user_playlist_remove_all_occurrences_of_tracks(self.user_id, from_id, tracks_to_move)

	def rename_playlist(self, old_playlist_name, new_playlist_name):
		self.client.user_playlist_change_details(self.user_id, self.get_playlist_id(old_playlist_name), new_playlist_name)

if __name__ == "__main__":
	my_client = SpotifyClient()
	my_client.connect()
	my_client.get_playlist_url("Song Roulette: July")
	exit()