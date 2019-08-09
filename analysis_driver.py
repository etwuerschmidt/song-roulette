import AnalysisClient.AnalysisClient
from SpotifyClient.SpotifyClient import SpotifyClient

sp_client = SpotifyClient()
sp_client.connect()
sp_client.sr_analysis = False
all_tracks = sp_client.get_playlist_tracks("Day Drive", fields='items(added_at,track(name))')
print(AnalysisClient.AnalysisClient.track_count_per_month(all_tracks, sp_client.sr_analysis))
