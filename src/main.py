from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import time
import datetime

from Tweet import Tweet
from detection.Early_detection import Early_detection
from relevance.Relevance_estimate import Relevance_estimate

consumer_key="a7vdFgIeOzMtv5SEf5Nw7euEy"
consumer_secret="FUeuYbCK3oatQ2zcUP4st7JvUZeVRCvFtChe9i4YOZgZPFS7k8"

access_token="2547796078-NukRjzi5dVONtf0H44KXoVwvVWINQ1q2PLCBsea"
access_token_secret="XIwJdgZsKZ5Dq8NlYsq4h7lrRmjyJJr9rCnC2uQTshGeS"

class StdOutListener(StreamListener):
	""" A listener handles tweets that are received from the stream.
	This is a basic listener that just prints received tweets to stdout.
	"""
	def __init__(self):
		self.count = 0
		self.start_time = time.time()

	def on_data(self, data):
		self.count += 1
		t = time.time() - self.start_time
		try:
			pass
			#print data #json encoded status
			"""
				type(data) == str
			"""

			##############TODO##############
			"""
				load data into Tweet
			"""
			tweet = Tweet()
			if not tweet.load(data):
				return


			##############TODO##############
			"""
				english detection, early relevant topic detection(zero term hited), RT handle, crawl external link
			"""
			if not tweet.isEnglish():
				return


			hited, hit_term = early_detection.early_topic_detection(tweet.text)
			if not hited:
				return

			try:
				if tweet.crawl_link_text() == 'Error':
					return
			except:
				print 'crawl_link_text Error...'
				return
			

			##############TODO##############

			relevant_topid, relevant_score = relevance_estimate.estimate(tweet) 
			"""
				if this tweet is relevant to one topic, then return this topicid and relevant_score;
				if this tweet is NOT relevant to any topic, then return (None, None)
			"""

			print '######################'
			print 'data rate:',self.count/t
			print 'hited: ', hit_term
			print tweet.text
			
			print relevant_topid, relevant_score
			if relevant_score < 0.5:
				return

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

			return
		except:
			print 'on_data() Error...'


	def on_error(self, status):
		print status

if __name__ == '__main__':
	#while main error
	early_detection = Early_detection()
	print 'early_detection init done...'
	relevance_estimate = Relevance_estimate()
	print  'relevance_estimate init done...'
	while True:
		try:
			l = StdOutListener()
			auth = OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_token, access_token_secret)
			stream = Stream(auth, l)
			print 'stream init done...'

			stream.sample()

			"""
			#tolerance
			while True:
				try:
					stream.sample()
				except Exception, e:
					print e
			"""
		except Exception, e:
			f = open('main_error_log.txt','a')
			print >> f, e, str(datetime.datetime.now())
			f.close()
			print 'main Error...'
