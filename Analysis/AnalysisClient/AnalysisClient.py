import datetime
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 

class Plotter():
    """Class to plot a variety of graphs"""
    
    def __init__(self, display=False, save=False):
        self.display = display
        self.save = save

    def bar_graph(self, x, y, xaxis=None, yaxis=None, title='bar_graph'):
        """Create a bar graph with provided information"""
        fig = go.Figure([go.Bar(x=list(x), y=list(y))])
        fig.update_layout(title=title,
                          xaxis_title=xaxis,
                          yaxis_title=yaxis)
        self.graph_view_save(fig)

    def graph_view_save(self, fig):
        if self.display:
            fig.show()
        if self.save:
            if not os.path.exists("images"):
                os.mkdir("images")
            image_name = fig.layout['title']['text'].replace(" ", "_")
            fig.write_image(f"images/{image_name}.png")

    def line_graph(self, x, y, xaxis=None, yaxis=None, title='line_graph'):
        """Create a line graph with provided information"""
        fig = go.Figure(data=go.Scatter(x=list(x), y=list(y)))
        fig.update_layout(title=title,
                          xaxis_title=xaxis,
                          yaxis_title=yaxis)
        self.graph_view_save(fig)

    def radar_graph(self, data, title='radar_graph'):
        """Create a radar graph with provided information"""
        df = pd.DataFrame(dict(r=list(data.values()), theta=list(data.keys())))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself')
        fig.update_layout(title=title)
        self.graph_view_save(fig)


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

def track_count_per_day(playlist_items, all_songs_sr_analysis=False):
    """Returns the amount of songs added to a playlist for each day of a month"""
    """One month of a playlist is passed in"""
    day_song_counter = {}
    days_in_curr_month = None
    for track in playlist_items:
        track_date = datetime.datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_in_curr_month = list(range(1,(datetime.date(track_date.year, track_date.month, 1) \
            - datetime.date(track_date.year, track_date.month - 1, 1)).days + 1)) if days_in_curr_month is None else days_in_curr_month
        while track_date.day > days_in_curr_month[0]:
            day_song_counter[f"{track_date.month - int(all_songs_sr_analysis)}/{days_in_curr_month[0]}"] = 0
            days_in_curr_month.pop(0)
        if f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.day}" in day_song_counter:
            day_song_counter[f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.day}"] += 1
        else:
            day_song_counter [f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.day}"] = 1
            days_in_curr_month.remove(track_date.day)
    return day_song_counter

def track_count_per_month(playlist_items, all_songs_sr_analysis=False):
    """Returns the amount of songs added to a playlist for each month"""
    """Full playlist is passed in"""
    month_song_counter = {}
    for track in playlist_items:
        track_date = datetime.datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
        if f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.year}" in month_song_counter:
            month_song_counter[f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.year}"] += 1
        else:
            month_song_counter[f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.year}"] = 1
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
    myPlot = Plotter(save=True)
    myPlot.line_graph([1,2,3], [1,2,3], title='Test Plot')
    exit()
