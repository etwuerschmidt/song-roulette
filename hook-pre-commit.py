from SpotifyClient.SpotifyClient import SpotifyClient
import sys

sp_client = SpotifyClient()
if sp_client.user_id != None or sp_client.username != None:
    try:
        raise ValueError("User information exposed.")
    except ValueError:
        print("Sensitive information from Spotify Client is about to be commited! Please check client files.")
        sys.exit(1)