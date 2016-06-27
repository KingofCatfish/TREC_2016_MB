from Tweet import Tweet
import pickle

class Tweets:
	'This class is for a set of tweets'

	#TODO
	def __init__(self, items = []):
		#if is a list of tweet class
		self.items = items

	#TODO
	def language_filter(self, lang = 'en'):
		pass

	#TODO
	def swear_word_filter(self):
		pass

	def import_from_pickled_data(self, filepath):
		self.items = []

		f = open(filepath, 'rb')
		loaded = pickle.load(f)

		for item in loaded:
			new_tweet = Tweet(id = item[1].id, timestamp = item[1].created_at, text = item[1].text)
			self.items.append(new_tweet)

	def peak(self, length = 3):
		text = ''
		for i in range(0, min(length, len(self.items))):
			text += 'id:' + str(self.items[i].id) + '\n'
			text += 'text:' + self.items[i].text + '\n'
			text += '\n'
		return text

	def __str__(self):
		return self.peak()
