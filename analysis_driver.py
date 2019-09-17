# Script for integration testing of analysis with Spotify playlists
import AnalysisClient.AnalysisClient
from AnalysisClient.AnalysisClient import Plotter
from SlackClient.SlackClient import SlackClient
from SpotifyClient.SpotifyClient import SpotifyClient

sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt')
sp_client.connect()
sp_client.sr_analysis = False

sl_client = SlackClient()
sl_client.connect()

all_tracks = sp_client.get_playlist_tracks("Song Roulette: September")
track_uris = sp_client.filter_tracks(all_tracks, 'uri')
audio_features = sp_client.get_audio_features(track_uris)

graph_draw = Plotter(display=True)
# avg_audio_features = AnalysisClient.AnalysisClient.avg_audio_features(audio_features)
# feature_plot = graph_draw.radar_graph(avg_audio_features, title="Test Graph")

# month_count = AnalysisClient.AnalysisClient.track_count_per_month(all_tracks, sp_client.sr_analysis, pad_to_today=True)
# month_plot = graph_draw.line_graph(month_count.keys(), month_count.values())

day_count = AnalysisClient.AnalysisClient.track_count_per_day(all_tracks, sp_client.sr_analysis, pad_to_month_end=True)
day_plot = graph_draw.line_graph(day_count.keys(), day_count.values())

# user_count = AnalysisClient.AnalysisClient.track_count_per_user(all_tracks)
# user_plot = graph_draw.bar_graph([f"User {key}" for key in user_count.keys()], user_count.values())

if graph_draw.save:
	sl_client.post_file("images/Test_Graph.png", message="Here's a test figure!")