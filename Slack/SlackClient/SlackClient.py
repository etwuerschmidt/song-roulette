import os
import slack

class SlackClient():

	def __init__(self):
		self.channel = '#sr-test'
		self.client = None
		self.client_token = os.environ['SLACK_OAUTH_TOKEN']

	def connect(self):
		self.client = slack.WebClient(token=self.client_token)

	def post_message(self, message, channel=None):
		response = self.client.chat_postMessage(channel=self.channel if not channel else channel, text=message)

	def set_channel(self, channel):
		self.channel = channel

if __name__ == "__main__":
	my_client = SlackClient()
	my_client.connect()
	my_client.post_message("hello world!")
	exit()