set search_path to :schema;
COMMIT;

TRUNCATE TABLE users CASCADE;
COMMIT;

TRUNCATE TABLE audio_features;
COMMIT;

TRUNCATE TABLE playlist_track_count CASCADE;
COMMIT;

TRUNCATE TABLE user_track_count;
COMMIT;