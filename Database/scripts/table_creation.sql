set search_path to :schema;
COMMIT;

CREATE TABLE users(
   id SERIAL PRIMARY KEY,
   spotify_id VARCHAR (50) UNIQUE NOT NULL
);
COMMIT;

CREATE TABLE audio_features(
	song_roulette_month DATE NOT NULL,
	acousticness FLOAT(8),
    danceability FLOAT(8),
    instrumentalness FLOAT(8),
    energy FLOAT(8),
    liveness FLOAT(8),
    speechiness FLOAT(8),
    valence FLOAT(8)
);
COMMIT;

CREATE TABLE playlist_track_count(
	date_added DATE NOT NULL,
	tracks_count INT
) PARTITION BY RANGE (date_added);
COMMIT;

CREATE TABLE playlist_track_count_y2019m9 
	PARTITION OF playlist_track_count
	FOR VALUES FROM ('2019-09-01') TO ('2019-10-01');
COMMIT;

CREATE TABLE user_track_count(
	user_id INT REFERENCES users(id),
	song_roulette_month DATE NOT NULL,
	track_count INT 
);
COMMIT;