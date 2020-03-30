from config import Config
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
import time

logging.basicConfig(format='%(levelname)s: [%(asctime)s][%(filename)s|%(funcName)s|%(lineno)s] %(message)s', level=logging.INFO)
logging.Formatter.converter = time.gmtime
date_format = "%m/%d/%Y %I:%M:%S %p"
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from slackapp import routes, models