import AnalysisClient.AnalysisClient as ac 
import argparse
import datetime
from datetime import date, timedelta
from SlackClient.SlackClient import SlackClient
from SpotifyClient.SpotifyClient import SpotifyClient

parser = argparse.ArgumentParser(description='Refresh monthly Spotify Playlist.')
parser.add_argument('--test', help='Perform a test run of the refresh script', action='store_true')
parser.add_argument('--live', help='Perform a live run of the refresh script. Specified day must match current day.', type=int)
parser.add_argument('--reset-test', help='Reset the testing playlists', action='store_true')
args = parser.parse_args()

def main():
	test = args.test or args.reset_test
	live_run_day = args.live
	day_of_month = date.today().day

	current_month_name = date.today().strftime("%B")
	last_month_name = (date.today() - (timedelta(weeks=5) if test else timedelta(live_run_day))).strftime("%B")
	playlist_prefix = "TEST " if test else "Song Roulette: "
	channel_name = "#sr-test" if test else "#dank-tunes"

	old_playlist_name = f"{playlist_prefix}{last_month_name}"
	all_playlist = f"{playlist_prefix}All Songs"
	new_playlist_name = f"{playlist_prefix}{current_month_name}"

	sl_client = SlackClient()
	sp_client = SpotifyClient(user_id=1269825738, username='Eric Wuerschmidt')
	sl_client.connect()
	sp_client.connect()

	if args.reset_test:
		sp_client.move_tracks(all_playlist, new_playlist_name)
		sp_client.rename_playlist(new_playlist_name, old_playlist_name)
		print(f"Songs from {all_playlist} were moved back to {old_playlist_name}")
	elif day_of_month == (day_of_month if test else live_run_day):
		#Analysis
		month_tracks = sp_client.get_playlist_tracks(old_playlist_name)
		user_count = ac.track_count_per_user(month_tracks)
		stats_message = ""
		for key, value in user_count.items():
			stats_message += f"User ID: {key} added {value} songs\n"
		
		#Spotify refresh
		if args.live:
			if input(f"You've specified a LIVE run. {old_playlist_name} will be moved to {all_playlist}. Enter Y to continue: ") != 'Y':
				exit()
		sp_client.move_tracks(old_playlist_name, all_playlist)
		sp_client.rename_playlist(old_playlist_name, new_playlist_name)
		current_playlist_link = sp_client.get_playlist_url(new_playlist_name)

		#Slack notification
		sl_client.set_channel(channel_name)
		sl_client.post_message(f"{playlist_prefix}{current_month_name} is now ready! Add songs here: {current_playlist_link}")
		sl_client.post_message(f"Thanks to everyone who contributed last month!\n{stats_message}")
		print("This was a test run. Check test playlists and channel.") if test else print("This was a LIVE run.")
	else:
		print(f"Please enter the current day ({day_of_month}) if you would like to refresh the monthly playlist. You entered {live_run_day}.")

main()
exit()