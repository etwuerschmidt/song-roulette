set search_path to :schema;
COMMIT;

DROP TABLE users CASCADE;
COMMIT;

DROP TABLE audio_features;
COMMIT;

DROP TABLE playlist_track_count CASCADE;
COMMIT;

DROP TABLE user_track_count;
COMMIT;