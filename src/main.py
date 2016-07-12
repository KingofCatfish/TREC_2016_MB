from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import time

consumer_key="a7vdFgIeOzMtv5SEf5Nw7euEy"
consumer_secret="FUeuYbCK3oatQ2zcUP4st7JvUZeVRCvFtChe9i4YOZgZPFS7k8"

access_token="2547796078-NukRjzi5dVONtf0H44KXoVwvVWINQ1q2PLCBsea"
access_token_secret="XIwJdgZsKZ5Dq8NlYsq4h7lrRmjyJJr9rCnC2uQTshGeS"

class StdOutListener(StreamListener):
	""" A listener handles tweets that are received from the stream.
	This is a basic listener that just prints received tweets to stdout.
	"""
	def on_data(self, data):
		print data #json encoded status

		##############TODO##############
		tweet = Tweet()
		tweet.load(data)
		#type(data) -> str

		##############TODO##############
		flag = early_detection(tweet) 
		"""
			english detection, early relevant topic detection(zero term hited), RT handle
		"""
		if flag == False:
			return

		##############TODO##############
		relevant_topid, relevant_score = relevance_estimate(tweet) 
		"""
			if this tweet is relevant to one topic, then return this topicid and relevant_score;
			if this tweet is NOT relevant to any topic, then return (None, None)
		"""
		if relevant_topid == None:
			return

		##############TODO##############
		flag = novelty_detection(tweet, relevant_topid)
		"""
			if this tweet is novel in this topic, return True;
			if this tweet is not novel, return False.
		"""
		if flag == False:
			return

		##############TODO##############
		a_push(tweet, relevant_topid, relevant_score)
		"""
			task a: push this tweet or not, depending on relevant_score
		"""

		##############TODO##############
		b_store(tweet, relevant_topid, relevant_score)
		"""
			task b: store this tweet and corresponding relevant_score
		"""

		return True

	def on_error(self, status):
		print(status)

if __name__ == '__main__':
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)

	#tolerance
	while True:
		try:
			stream.sample()
		except Exception, e:
			print e
