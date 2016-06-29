from Tweet import Tweet
from Tweets import Tweets
import pickle
import NOVELTY_DETECTION_RECOVERY_FILE from config

class novelty_detection:
	'''
		This class is for novelty detection.

		Sample Usage:

		import novelty_detection as nd

		detector = nd.novelty_detection('naive', 'production')
		detector.config(naive_valve = 0.6)

		for t in tweets:
			if detector.stream(t):
				report(t)
	'''

	method_list = {
		'naive' : {
			'method_name' : 'naive similarity detection',
			'parameter' : {
				'naive_valve' : 0.6
			},
			'callback_name' : 'naive_stream'
		},
		'simhash' : {
			'method_name' : 'Simhash similarity detection',
			'parameter' : {
				'simhash_valve' : 5
			},
			'callback_name' : 'simhash_stream'
		},
		'sample method' : {
			'method_name' : 'just a sample method',
			'parameter' : {
				'parameter1' : 1,
				'parameter2' : 2
			},
			'callback_name' : 'sample_stream'
		}
	}
	
	def __init__(self, method, environment = 'debug'):
		if method in novelty_detection.method_list:
			self.method = novelty_detection.method_list[method]['method_name']
			self.reported = []
			self.parameter = novelty_detection.method_list[method]['parameter']
			self.stream_callback = getattr(self, novelty_detection.method_list[method]['callback_name'])
			if self.environment != 'debug':
				self.environment = 'production'
			else:
				self.environment = 'debug'
			self.reload()
		else:
			raise Exception('novelty_detection does not support ' + str(method))

	def __str__(self):
		return 'Novelty Detector with ' + self.method

	def reload(self):
		if self.environment == 'debug':
			return

		try:
			recovery_file = open(NOVELTY_DETECTION_RECOVERY_FILE, 'rb')
			recovery_data = recovery_file.read()
			self.reported = pickle.load(recovery_data)
			recovery_file.close()
		except IOError:
			recovery_file = open(NOVELTY_DETECTION_RECOVERY_FILE, 'wb')
			recovery_file.close()

	def backup(self):
		recovery_file = open(NOVELTY_DETECTION_RECOVERY_FILE, 'wb')
		pickle.dump(self.reported, recovery_file)
		recovery_file.close()


	def config(self, **arg):
		for key, value in arg.iteritems():
			if key in self.parameter:
				self.parameter[key] = value

	def stream(self, tweet):
		'''
			Return Ture if novelty detected, otherwise return False.
		'''
		if not isinstance(tweet, Tweet):
			raise Exception('Try to cluster a non-tweet instance')

		ret = self.stream_callback(tweet)
		if ret:
			self.reported.append(tweet)
			if self.production == 'production':
				self.bakcup()
		return ret

	def naive_stream(self, tweet):
		for doc in self.reported:
			if doc.naive_similarity(tweet, doc) > self.parameter['naive_valve']:
				return False
		
		return True

	def simhash_stream(self, tweet):
		for doc in self.reported:
			if doc.simhash_similarity(tweet, doc) > self.parameter['simhash_valve']:
				return False

		return True

	#TODO
	def auto_tuning(self, Tweets):
		pass


# nd = novelty_detection('test')