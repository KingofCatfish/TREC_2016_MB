from Tweet import Tweet

class novelty_detection:
	'''
		This class is for novelty detection.

		Sample Usage:

		import novelty_detection as nd

		detector = nd.novelty_detection('naive')
		detector.config(value = 0.6)

		for t in tweets:
			if detector.stream(t):
				report(t)
	'''

	method_list = {
		'naive' : {
			'method_name' : 'naive similarity detection',
			'parameter' : {
				'naive_valve' : 0.6
			}
		}
	}
	
	def __init__(self, method):
		if method in novelty_detection.method_list:
			self.method = novelty_detection.method_list[method]['method_name']
			self.reported = []

			if method == 'naive':
				self.parameter = novelty_detection.method_list[method]['parameter']
		else:
			raise Exception('novelty_detection does not support ' + str(method))

	def __str__(self):
		return 'Novelty Detector with ' + self.method

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

		if self.method == novelty_detection.method_list['naive']['method_name']:
			return self.naive_stream(tweet)

	def naive_stream(self, tweet):
		for doc in self.reported:
			if doc.naive_similarity(tweet, doc) > self.parameter['naive_valve']:
				return False

		self.reported.append(tweet)
		return True



# nd = novelty_detection('test')