from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import time
import datetime
import copy

from Tweet import Tweet

from detection.Early_detection import Early_detection
from detection.Necessary_detection import Necessary_detection
from relevance.Relevance_estimate import Relevance_estimate
from push.Push import Push

from novelty_detectors import novelty_detectors

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
			"""
				type(data) == str
			"""
			#print data #json encoded status

			##############TODO##############
			"""
				load data into Tweet
			"""
			tweet.reset()
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

			candidate_topid, relevant_title = necessary_detection.nec_detection(tweet.text)
			if candidate_topid == None:
				return

			try:
				if tweet.crawl_link_text() == 'Error':
					return
			except:
				print 'crawl_link_text Error...'
				return
			

			##############TODO##############

			#relevant_topid, relevant_score, relevant_title = relevance_estimate.estimate(tweet) 
			relevant_topid, relevant_score = relevance_estimate.sniper_estimate(tweet, candidate_topid)
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

			##############TODO##############
			"""
				check push quota and push strategy
			"""
			if not push.a_push_ok(tweet.id, relevant_topid, relevant_score):
				return

			##############TODO##############
			t = copy.deepcopy(tweet)

			#rmove # RT http://
			t.remove_verbose()
			print t.clean_text

			#t.clean_text is a clean text without # RT http://
			novel = novelty_detectors.novelty_detect(t, relevant_topid)
			
				#if this tweet is novel in this topic, return True;
				#if this tweet is not novel, return False.
			
			if not novel:
				print 'Not Novel...'
				return
			print 'Novel...'

			##############TODO##############
			url, status_code, response_text = push.a_push(tweet.id, relevant_topid)
			"""
				task a: push this tweet
			"""

			##############TODO##############
			push.b_store(tweet.id, relevant_topid, relevant_score)
			"""
				task b: store this tweet and corresponding relevant_score
			"""
			f = open('./push/a_push_log.txt','a')
			print >> f, '*************************'
			print >> f, relevant_topid, relevant_score, tweet.id
			print >> f, relevant_title
			print >> f, tweet.text
			print >> f, 'remove verbose: ', t.clean_text
			print >> f, url
			print >> f, 'status_code:',status_code
			print >> f, 'response_text:', response_text
			f.close()


			return

		except Exception, e:
			print e
			print 'on_data() Error...'


	def on_error(self, status):
		print status

if __name__ == '__main__':
	#while main error
	tweet = Tweet()
	print 'tweet init done...'

	early_detection = Early_detection()
	print 'early_detection init done...'

	necessary_detection = Necessary_detection()
	print 'necessary_detection init done...'

	relevance_estimate = Relevance_estimate()
	print  'relevance_estimate init done...'

	novelty_detectors = novelty_detectors()
	novelty_detectors.refresh()
	print 'novelty_detectors init done...'
	
	push = Push()
	print 'push init done...'

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
