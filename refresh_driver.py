import AnalysisClient.AnalysisClient as ac 
import datetime
from datetime import date, timedelta
from SlackClient.SlackClient import SlackClient
from SpotifyClient.SpotifyClient import SpotifyClient

test = True
live_run_day = 1

day_of_month = date.today().day

current_month_name = date.today().strftime("%B")
last_month_name = (date.today() - (timedelta(weeks=5) if test else timedelta(live_run_day))).strftime("%B")
playlist_prefix = "TEST " if test else "Song Roulette: "
channel_name = "#sr-test" if test else "#dank-tunes"

if day_of_month == (day_of_month if test else live_run_day):
	old_playlist_name = f"{playlist_prefix}{last_month_name}"
	all_playlist = f"{playlist_prefix}All Songs"
	new_playlist_name = f"{playlist_prefix}{current_month_name}"

	sl_client = SlackClient()
	sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt')
	sl_client.connect()
	sp_client.connect()

	month_tracks = sp_client.get_playlist_tracks(old_playlist_name)
	sp_client.move_tracks(old_playlist_name, all_playlist)
	sp_client.rename_playlist(old_playlist_name, new_playlist_name)
	current_playlist_link = sp_client.get_playlist_url(new_playlist_name)

	user_count = ac.track_count_per_user(month_tracks)

	sl_client.set_channel(channel_name)
	sl_client.post_message(f"{playlist_prefix}{current_month_name} is now ready! Add songs here: {current_playlist_link}")
	stats_message = ""
	for key, value in user_count.items():
		stats_message += f"User ID: {key} added {value} songs\n"
	sl_client.post_message(f"Thanks to everyone who contributed last month!\n{stats_message}")
	print("This was a test run. Check test playlists and channel. Flip test bool for live run.") if test else print("This was a LIVE run.")
else:
	print("The playlist shouldn't be refreshed today!")
exit()