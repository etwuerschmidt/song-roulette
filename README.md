# Song-Roulette
Refresh monthly collaborative playlist and retrieve information for analysis using Spotipy. Alert users in Slack of updates / respond to inquries.

To get started, run
```bash
./install.sh
```

and update the following property to setup applicable git hooks
```bash
git config core.hooksPath .githooks
```

The following additional installations are needed:
  - Orca for saving Plotly figures https://github.com/plotly/orca
  - Heroku CLI for hosted DB https://devcenter.heroku.com/articles/heroku-cli
  - Postgres for local DB validation https://www.enterprisedb.com/downloads/postgres-postgresql-downloads#windows