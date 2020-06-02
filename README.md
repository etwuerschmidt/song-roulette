# Song-Roulette
[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)

Refresh monthly collaborative playlist and retrieve information for analysis using Spotipy. Alert users in Slack of updates / respond to inquries.

To get started, run:

```
> $env:FLASK_APP = "song_roulette.py"
> $env:FLASK_ENV="development"
> ./venv/Scripts/activate
> flask run
 * Serving Flask app "song_roulette.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 127-141-204
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

 # In a separate terminal
 > ./ngrok http 5000
 ...
 Forwarding                    http://XXX.ngrok.io -> http://localhost:5000 

 # Update Slash Command endpoint at https://api.slack.com/apps for the appropriate slash command
 ```

The following installations are needed:
  - Orca for saving Plotly figures https://github.com/plotly/orca
  - Heroku CLI for hosted DB https://devcenter.heroku.com/articles/heroku-cli
  - Postgres for local DB validation https://www.enterprisedb.com/downloads/postgres-postgresql-downloads#windows
  - ngrok for localhost endpoint exposure https://ngrok.com/download