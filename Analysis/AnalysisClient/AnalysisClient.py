import datetime
import pandas as pd
import plotly.express as px

class Plotter():
    """Used to plot information processed by functions below"""
    def __init__(self):
        self.name = "Plotter"

    def radar_plot():
        exit()
        # af = my_client.get_audio_features(filtered_tracks)
        # df = pd.DataFrame(dict(r=list(af.values()), theta=list(af.keys())))
        # fig = px.line_polar(df,r='r', theta='theta', line_close=True)
        # fig.update_traces(fill='toself', name='Audio Features: July')
        # fig.show()

def avg_audio_features(song_features):
    """Returns the avg audio features for a given list of songs"""
    avg_features = {"acousticness": 0,
                    "danceability": 0,
                    "instrumentalness": 0,
                    "energy": 0,
                    "liveness": 0,
                    "speechiness": 0,
                    "valence": 0}
    for song_feature in song_features:
        for feature, value in song_feature.items():
            if feature in avg_features.keys():
                avg_features[feature] += value
    for key, value in avg_features.items():
        avg_features[key] = value / len(song_features)
    return avg_features

def track_count_per_month(playlist_items, sr_analysis=True):
    """Returns the amount of songs added to a playlist for each month"""
    month_song_counter = {}
    for track in playlist_items:
        track_date = datetime.datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
        if f"{track_date.month - int(sr_analysis)}/{track_date.year}" in month_song_counter:
            month_song_counter[f"{track_date.month - int(sr_analysis)}/{track_date.year}"] += 1
        else:
            month_song_counter[f"{track_date.month - int(sr_analysis)}/{track_date.year}"] = 1
    return month_song_counter

def track_count_per_user(playlist_items):
    """Returns the amount of songs per user that were added to a playlist"""
    user_song_counter = {}
    for track in playlist_items:
        if track['added_by']['id'] in user_song_counter:
            user_song_counter[track['added_by']['id']] += 1
        else:
            user_song_counter[track['added_by']['id']] = 1
    return user_song_counter

if __name__ == "__main__":
    exit()
