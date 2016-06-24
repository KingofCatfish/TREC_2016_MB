from Tweet import Tweet

class novelty_detection:
	def __init__(self, method):
		self.method = method

	def config(self, **arg):
		pass

	def stream(self, tweet):
		if not isinstance(tweet, Tweet):
			raise Exception('Try to cluster a non-tweet instance')


# nd = novelty_detection('test')