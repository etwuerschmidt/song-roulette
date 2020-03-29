from calendar import monthrange
import chart_studio
import chart_studio.plotly as plot
import collections
import datetime
from datetime import date
import logging
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import uuid

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class Plotter():
    """Class to plot a variety of graphs"""

    def __init__(self, display=False, host_online=True):
        self.display = display
        self.host_online = host_online
        if not self.host_online:
            try:
                subprocess.run(["orca", "--version"], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=True)
            except:
                print("Orca is not installed or is not in PATH! Saving images locally is not supported. Setting Plotter to host images online.")
                self.host_online = True
        chart_studio.tools.set_credentials_file(
            username='etwuerschmidt', api_key=os.environ['CHART_STUDIO_KEY'])

    def bar_graph(self, x, y, xaxis=None, yaxis=None, title='bar_graph'):
        """Create a bar graph with provided information"""
        fig = go.Figure([go.Bar(x=list(x),
                                y=list(y),
                                text=list(y),
                                textposition='auto')])
        fig.update_layout(title=title,
                          xaxis_title=xaxis,
                          yaxis_title=yaxis,
                          yaxis={'tickformat': ',d'})
        return self.graph_view_save(fig)

    def graph_view_save(self, fig):
        image_name = "{0} {1}".format(fig.layout['title']['text'], str(uuid.uuid1())).replace(
            " ", "_").replace(":", "_").replace("/", "_")
        url = None
        if self.display:
            fig.show()
        if self.host_online:
            url = plot.plot(fig, filename=image_name, auto_open=False)
            logging.info(f"Image successfully created and hosted at {url}")
        else:
            if not os.path.exists("images"):
                os.mkdir("images")
            fig.write_image(f"images/{image_name}.png")
        return url

    def line_graph(self, x, y, xaxis=None, yaxis=None, title='line_graph'):
        """Create a line graph with provided information"""
        logging.info(f"Creating line graph with title {title}")
        fig = go.Figure(data=go.Scatter(x=list(x), y=list(y)))
        fig.update_layout(title=title,
                          xaxis_title=xaxis,
                          yaxis_title=yaxis,
                          yaxis={'tickformat': ',d'})
        return self.graph_view_save(fig)

    def radar_graph(self, data, title='radar_graph'):
        """Create a radar graph with provided information"""
        df = pd.DataFrame(dict(r=list(data.values()), theta=list(data.keys())))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself')
        fig.update_layout(title=title)
        return self.graph_view_save(fig)


def avg_audio_features(song_features):
    """Returns the avg audio features for a given list of songs"""
    logging.info("Calculating average audio features")
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


def track_count_per_day(playlist_items, pad_to_today=False, pad_to_month_end=False):
    """Returns the amount of songs added to a playlist for each day of a month"""
    """One month of a playlist is passed in"""
    logging.info("Calculating track count per day")
    prev_track_date = datetime.datetime.strptime(
        playlist_items[0]['added_at'], '%Y-%m-%dT%H:%M:%SZ')
    day_song_counter = {}
    days_in_curr_month = list(
        range(1, monthrange(prev_track_date.year, prev_track_date.month)[1] + 1))
    for track in playlist_items:
        track_date = datetime.datetime.strptime(
            track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
        while len(days_in_curr_month) > 0 and track_date.day > days_in_curr_month[0]:
            day_song_counter[f"{track_date.month}/{days_in_curr_month[0]}"] = 0
            days_in_curr_month.pop(0)
        if f"{track_date.month}/{track_date.day}" in day_song_counter:
            day_song_counter[f"{track_date.month}/{track_date.day}"] += 1
        else:
            day_song_counter[f"{track_date.month}/{track_date.day}"] = 1
            days_in_curr_month.remove(track_date.day)
        prev_track_date = track_date
    if pad_to_today or pad_to_month_end:
        day_range = 0
        if pad_to_today:
            day_range = list(range(prev_track_date.day+1, date.today().day+1))
        elif pad_to_month_end:
            day_range = list(range(
                prev_track_date.day+1, monthrange(prev_track_date.year, prev_track_date.month)[1] + 1))
        while day_range:
            day_song_counter[f"{prev_track_date.month}/{day_range[0]}"] = 0
            day_range.pop(0)
    return day_song_counter


def track_count_per_month(playlist_items, all_songs_sr_analysis=False, pad_to_today=False):
    """Returns the amount of songs added to a playlist for each month"""
    """Full playlist is passed in"""
    logging.info("Calculating track count per month")
    prev_track_date = datetime.datetime.strptime(
        playlist_items[0]['added_at'], '%Y-%m-%dT%H:%M:%SZ')
    month_song_counter = {}
    month_range = list(range(prev_track_date.month, 13))
    for track in playlist_items:
        track_date = datetime.datetime.strptime(
            track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
        prev_track_year = prev_track_date.year
        while track_date.year != prev_track_year:
            while month_range:
                month_song_counter[f"{month_range[0] - int(all_songs_sr_analysis)}/{prev_track_year}"] = 0
                month_range.pop(0)
            prev_track_year += 1
            month_range = list(range(1, 13))
        prev_track_date = track_date
        while len(month_range) > 0 and track_date.month > month_range[0]:
            month_song_counter[f"{month_range[0] - int(all_songs_sr_analysis)}/{track_date.year}"] = 0
            month_range.pop(0)
        if f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.year}" in month_song_counter:
            month_song_counter[f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.year}"] += 1
        else:
            month_song_counter[f"{track_date.month - int(all_songs_sr_analysis)}/{track_date.year}"] = 1
            month_range.remove(track_date.month)
    if pad_to_today:
        year_pad = False
        prev_track_year = prev_track_date.year
        while date.today().year != prev_track_year:
            year_pad = True
            while month_range:
                month_song_counter[f"{month_range[0] - int(all_songs_sr_analysis)}/{prev_track_year}"] = 0
                month_range.pop(0)
            prev_track_year += 1
            month_range = list(range(1, 13))
        month_range = list(range(prev_track_date.month+1, date.today().month+1)
                           ) if not year_pad else list(range(1, date.today().month+1))
        while month_range:
            month_song_counter[f"{month_range[0]}/{date.today().year}"] = 0
            month_range.pop(0)
    return month_song_counter


def track_count_per_user(playlist_items):
    """Returns the amount of songs per user that were added to a playlist"""
    logging.info("Calculating track count per user")
    user_song_counter = {}
    for track in playlist_items:
        if track['added_by']['id'] in user_song_counter:
            user_song_counter[track['added_by']['id']] += 1
        else:
            user_song_counter[track['added_by']['id']] = 1
    user_song_counter = collections.OrderedDict(
        sorted(user_song_counter.items(), key=lambda item: item[1], reverse=True))
    return user_song_counter


if __name__ == "__main__":
    myPlot = Plotter()
    url = myPlot.line_graph([1, 2, 3], [1, 2, 3], title='Test Plot')
    exit()
