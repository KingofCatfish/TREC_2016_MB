from Tweet import Tweet
from collections import Sequence
import pickle

class Tweets(Sequence):
	'This class is for a set of tweets'

	#TODO
	def __init__(self, *data):
		#if is a list of tweet class
		self.items = list(data)

	def __getitem__(self, key):
		return self.items[key]

	def __len__(self):
		return len(self.items)

#	def __iter__(self):


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
