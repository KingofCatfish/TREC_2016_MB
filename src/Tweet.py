
class Tweet:
	'This class is for storage of Tweet data'

	def __init__(self, id, timestamp, content, lang):
		self.id = id
		self.timestamp = timestamp
		self.content = content
		self.language = lang

	#TODO
	def similarity1(TweetA, TweetB):
		'A static method for measuring the similarity between two tweets'
		pass