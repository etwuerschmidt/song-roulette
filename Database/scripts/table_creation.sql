set search_path to test;

CREATE TABLE users(
   id serial PRIMARY KEY,
   spotify_id VARCHAR (50) UNIQUE NOT NULL
);