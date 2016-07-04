from __future__ import division
import nltk
import Tweet
import math
from nltk.corpus import brown
from nltk.corpus import twitter_samples 

'''

'''

class formality_detector():
	def __init__(self):

		twitter = twitter_samples.strings('tweets.20150430-223406.json')
		news = brown.words(categories='news')

		twitter = Tweet.Tweet(text = ' '.join(twitter)).stem()
		news = Tweet.Tweet(text = ' '.join(news)).stem()

		self.twitter_freq = nltk.FreqDist(twitter)
		self.tsum = len(twitter)
		self.news_freq = nltk.FreqDist(news)
		self.nsum = len(news)

	def check(self, tweet):
		if not isinstance(tweet, Tweet.Tweet):
			raise Exception('only accept tweet object')

		zero_map = 0.1
		score_list = []
		weight_list = []
		for word in tweet.stem():
			tf = self.twitter_freq[word]
			nf = self.news_freq[word]

			if tf == 0:
				tf = zero_map
			if nf == 0:
				nf = zero_map

			weight = -1 * math.log((nf + tf) / (self.tsum + self.nsum))
			weight_list.append(weight)
			score = nf * self.tsum - tf * self.nsum
			score_list.append([weight, score])

		if weight_list == []:
			return 0

		weight_min = min(weight_list)
		weight_max = max(weight_list)

		if weight_max == weight_min:
			result = 0
			for weight, score in score_list:
				result += score
			return result / (len(score_list) * self.tsum * self.nsum)

		weight_sum = 0
		for weight,score in score_list:
			weight_sum += ((weight - weight_min) / (weight_max - weight_min))

		result = 0
		for weight, score in score_list:
			result += score * (((weight - weight_min) / (weight_max - weight_min)) / weight_sum)

		result /= self.tsum * self.nsum
		return result

def run(fd, text):
	t = Tweet.Tweet(text = text)
	print fd.check(t)

if __name__ == '__main__':
	fd = formality_detector()
	test_case = [
		'This is a sample text', 
		'The Reuters Corpus contains 10,788 news documents totaling 1.3 million words.',
		'Happy #CanadaDay! Enjoy a mini-marathon of Canadian themed South Park episodes tonight at 8 PM EST!',
		'Happy Canada Day. Do your Canada dance.',
		'OMG, this is fucking awesome'
	]
	for item in test_case:
		print item
		print fd.check(Tweet.Tweet(text = item))