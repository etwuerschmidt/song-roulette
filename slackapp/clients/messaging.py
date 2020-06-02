import time
import slack
import os
from datetime import datetime
from slackapp import app, date_format
import sys
sys.path.append('..')

slack_error_msg = "Something went wrong at {0} UTC! <@{1}>, please check the logs to figure out what happened."


class SlackClient():
    """Class for handling all Slack messaging"""

    def __init__(self, **kwargs):
        """Initializes an object with all necessary items to create a Slack Client"""
        self.admin = "U8WRDEPRT"
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
        except slack.errors.SlackApiError as block_error:
            app.logger.exception(block_error)
            timestamp = datetime.utcnow().strftime(date_format)
            replacement_block_msg = f"Looks like there's been an issue embeddeding the image, but you can still view it at {blocks[0]['image_url']}"
            self.post_message(replacement_block_msg)
        except:
            app.logger.exception(sys.exc_info()[0])
            timestamp = datetime.utcnow().strftime(date_format)
            self.post_message(slack_error_msg.format(timestamp, self.admin))

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
            timestamp = datetime.utcnow().strftime(date_format)
            self.post_message(slack_error_msg.format(timestamp, self.admin))

    def set_channel(self, channel):
        """Sets the channel for messages to be posted to"""
        self.channel = channel


if __name__ == "__main__":
    my_client = SlackClient()
    my_client.connect()
    my_client.post_message("hello world!")
    exit()
