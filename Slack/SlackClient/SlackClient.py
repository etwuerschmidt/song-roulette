import os
import slack

class SlackClient():
    """Class for handling all Slack messaging"""

    def __init__(self):
        """Initializes an object with all necessary items to create a Slack Client"""
        self.channel = '#sr-test'
        self.client = None
        self.client_token = os.environ['SLACK_OAUTH_TOKEN']

    def connect(self):
        """Authentication for Slack Client"""
        self.client = slack.WebClient(token=self.client_token)

    def post_message(self, message, channel=None):
        """Writes specified message to either default or specified channel"""
        self.client.chat_postMessage(channel=self.channel if not channel else channel, text=message)

    def set_channel(self, channel):
        """Sets the channel for messages to be posted to"""
        self.channel = channel

if __name__ == "__main__":
    my_client = SlackClient()
    my_client.connect()
    my_client.post_message("hello world!")
    exit()