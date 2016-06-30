from __future__ import division
import nltk
import Tweet
from nltk.corpus import brown
from nltk.corpus import twitter_samples 


class formality_detector():
	def __init__(self, prior = 0.5):
		'''
		The prior argument is the prior probability of formal text of input
		'''
		self.prior = prior

		twitter = twitter_samples.strings('tweets.20150430-223406.json')
		news = brown.words(categories='news')

		twitter_word = []
		count = 0
		for item in twitter:
			count += 1
			if round(count / len(twitter), 2) != round((count - 1) / len(twitter), 2):
				print str(100 * round(count / len(twitter), 2)) + '% completed'
			t = Tweet.Tweet(text = item)
			twitter += t.stem()

		news = Tweet.Tweet(text = ' '.join(news)).stem()

		self.twitter_freq = nltk.FreqDist(twitter)
		self.tsum = len(twitter)
		self.news_freq = nltk.FreqDist(news)
		self.nsum = len(news)

	def check(self, tweet):
		if not isinstance(tweet, Tweet):
			raise Exception('only accept tweet object')

		zero_map = 0.1
		score = 1
		for word in tweet.stem():
			if self.twitter_freq[word] == 0:
				cond_freq = zero_map / self.tsum
			else:
				cond_freq = self.twitter_freq[word] / self.tsum

			if self.news_freq[word] == 0:
				freq = zero_map / self.nsum
			else:
				freq = self.news_freq[word] / self.nsum

			score *= (cond_freq / preq)

		return score * self.prior


if __name__ == '__main__':
	fd = formality_detector()