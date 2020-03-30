import sys
sys.path.append('..')
from slackapp import app, date_format
from datetime import datetime
import os
import slack
import time


class SlackClient():
    """Class for handling all Slack messaging"""

    def __init__(self, **kwargs):
        """Initializes an object with all necessary items to create a Slack Client"""
        self.channel = "CLYHQ9SQM"
        self.client = None
        self.client_token = kwargs.get(
            'SLACK_OAUTH_TOKEN', os.environ['SLACK_OAUTH_TOKEN'])

    def connect(self):
        """Authentication for Slack Client"""
        self.client = slack.WebClient(token=self.client_token)

    def post_block(self, blocks, channel=None):
        """Posts specified blocks to either default or specified channel"""
        try:
            self.client.chat_postMessage(
            channel=self.channel if not channel else channel, blocks=blocks)
        except Exception as e:
            app.logger.exception(e)
            timestamp = datetime.utcnow().strftime(date_format)
            post_message(f"Something went wrong at {timestamp} UTC! Please check the logs to figure out what happened.")

    def post_file(self, filename, message=None, channel=None):
        """Posts specified file to either default or specified channel with specified comment"""
        self.client.files_upload(channels=self.channel if not channel else channel, file=filename,
                                 initial_comment=f"Song Roulette Bot is posting on Eric's behalf: {message}")

    def post_message(self, message, channel=None):
        """Writes specified message to either default or specified channel"""
        try:
            self.client.chat_postMessage(
                channel=self.channel if not channel else channel, text=message)
        except Exception as e:
            app.logger.exception(e)
            timestamp=datetime.utcnow().strftime(date_format)
            post_message(f"Something went wrong at {timestamp} UTC! Please check the logs to figure out what happened.")


    def set_channel(self, channel):
        """Sets the channel for messages to be posted to"""
        self.channel=channel


if __name__ == "__main__":
    my_client=SlackClient()
    my_client.connect()
    my_client.post_message("hello world!")
    exit()
