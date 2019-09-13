# Script for integration testing of analysis with Spotify playlists
import AnalysisClient.AnalysisClient
from AnalysisClient.AnalysisClient import Plotter
from SpotifyClient.SpotifyClient import SpotifyClient

sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt')
sp_client.connect()
sp_client.sr_analysis = False

all_tracks = sp_client.get_playlist_tracks("Song Roulette: August", fields='items(added_at,added_by,track(name,uri))')
track_uris = sp_client.filter_tracks(all_tracks, 'uri')
audio_features = sp_client.get_audio_features(track_uris)

graph_draw = Plotter(display=True)
avg_audio_features = AnalysisClient.AnalysisClient.avg_audio_features(audio_features)
feature_plot = graph_draw.radar_graph(avg_audio_features)

day_count = AnalysisClient.AnalysisClient.track_count_per_day(all_tracks, sp_client.sr_analysis)
day_plot = graph_draw.line_graph(day_count.keys(), day_count.values())

user_count = AnalysisClient.AnalysisClient.track_count_per_user(all_tracks)
user_plot = graph_draw.bar_graph([f"User {key}" for key in user_count.keys()], user_count.values())
