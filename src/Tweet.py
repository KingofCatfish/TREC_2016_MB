from __future__ import division
import nltk
import re
import string
import urllib2
import urllib
import unicodedata
import signal
import time
import json
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from simhash import Simhash
import langdetect
import requests
import eventlet

class Tweet:
	'This class is for storage of Tweet data'

	def __init__(self, text=None, id=None, timestamp=None, retweet_count=None, \
				user_friends_count=None, user_followers_count=None, \
				user_statuses_count=None, topicid = None, created_at = None):
		self.id = id
		self.timestamp = timestamp
		self.text = text
		self.retweet_count = retweet_count
		self.friends_count = user_friends_count
		self.followers_count = user_followers_count
		self.statuses_count = user_statuses_count
		self.topicid = topicid
		self.link_text = ''
		self.isLink = False
		self.created_at = created_at
		self.clean_text = None

		self.stemmed = []

	def __str__(self):
		return self.text

	def reset(self):
		self.id = None
		self.timestamp = None
		self.text = None
		self.retweet_count = None
		self.friends_count = None
		self.followers_count = None
		self.statuses_count = None
		self.topicid = None
		self.link_text = None
		self.isLink = False
		self.created_at = None
		self.clean_text = None

		self.stemmed = []

	def remove_verbose(self):
		verbose_text = self.text
		#####remove hashtag#####
		verbose_text = re.sub(r'#[^\s]+', '', verbose_text)
		#####remove @ #####
		verbose_text = re.sub(r'@[^\s]+', '', verbose_text)
		#####remove all term behind http#####
		verbose_text = re.sub(r'http\S+', '', verbose_text)

		self.clean_text = verbose_text


	def load(self, data_s):
		try:
			"""
				maybe delete or field empty.
			"""
			if len(data_s) < 200:
				return False
			data = json.loads(data_s)
			if data['user']['lang'] != 'en':
				return False
			self.id = data['id']
			self.created_at = data['created_at']
			self.raw = data['text']
			self.text = data['text'].encode('ascii', 'ignore')
			self.retweet_count = data['retweet_count']
			self.friends_count = data['user']['friends_count']
			self.followers_count = data['user']['followers_count']
			self.statuses_count = data['user']['statuses_count']
			self.clean_text = None
			return True
		except Exception, e:
			return False


	def load_tweepy(self, data):
		self.id = data.id
		self.created_at = data.created_at
		self.raw = data.text
		self.text = data.text.encode('ascii', 'ignore')
		self.clean_text = None
		self.retweet_count = data.retweet_count
		self.friends_count = data.user.friends_count
		self.followers_count = data.user.followers_count
		self.statuses_count = data.user.statuses_count
		return self

	def config(self, **arg):
		for key, value in arg.iteritems():
			if hasattr(self, key):
				setattr(self, key, value)
			else:
				print str(key) + ' does not exist'


	@staticmethod
	def naive_similarity(TweetA, TweetB):
		'''
			Assume Tweet A includes {m} words, each word has {mi} character. Tweet B\
			has {n} words, each word has {ni} character. The similarity between A and\
			B is measured by the weighted intersection score divided by union score.

			For instance:
				Tweet A : I had had a cat.
				Tweet B : A cat had another cat.
			
				The intersection: i had had a cat a cat had another cat
				The union: had a cat a cat had

				The intersection score : 1 + 3 + 3 + 1 + 3 + 1 + 3 + 3 + 7 + 3 = 28
				The union score : 3 + 1 + 3 + 1 + 3 + 3 = 14
				Similarity = 15 / 28 = 0.5
		'''
		if not isinstance(TweetA, Tweet) or not isinstance(TweetB, Tweet):
			raise Exception('can only calculate similarity between Tweet object')

		wordlistA = TweetA.stem_text()
		wordlistB = TweetB.stem_text()

		intScore = 0
		uniScore = 0
		for word in wordlistA:
			intScore += len(word)
		for word in wordlistB:
			intScore += len(word)

		templist = []
		for word in wordlistB:
			templist.append(word)

		for word in wordlistA:
			if word in templist:
				uniScore += 2 * len(word)
				templist.remove(word)

		if uniScore == 0:
			return 0
		else:
			return uniScore / intScore

	@staticmethod
	def simhash_similarity(TweetA, TweetB):
		if not isinstance(TweetA, Tweet) or not isinstance(TweetB, Tweet):
			raise Exception('can only calculate similarity between Tweet object')

		textA = ' '.join(TweetA.stem())
		textB = ' '.join(TweetB.stem())
		return Simhash(textA).distance(Simhash(textB))

	@staticmethod
	def jaccard_distance(TweetA, TweetB):
		if not isinstance(TweetA, Tweet) or not isinstance(TweetB, Tweet):
			raise Exception('can only calculate similarity between Tweet object')
		tA = TweetA.stem()
		tB = TweetB.stem()

		return 1 - (len(set(ta) & set(tb)) / len(set(ta) | set(tb)))

	#crawl the web text from external link
	def crawl_link_text(self):

		def handler(signo, frame):
			raise Exception("end of time")


		text = self.text
		eventlet.monkey_patch() 

		try:
			if 'https://t.co/' in text:
				url = text[text.find('http'):text.find('http')+23].encode('ascii', 'ignore')
			elif 'http://t.co/' in text:
				url = text[text.find('http'):text.find('http')+22].encode('ascii', 'ignore')
			else:
				self.link_text = self.text
				self.isLink = False
				return 'No_link'

			print url
			if len(url) < 20:
				return 'Error'
			
			with eventlet.Timeout(8):
				"""
					 can only detect timeouts in "greenthreaded" code
					 you cannot time out CPU-only operations with this class
				"""
				try:
					response = requests.get(url, verify=True)
					html = response.text
					clean_html = re.sub(r'<.*?>', '', html)
					self.link_text = clean_html

					self.isLink = True
					return 'Done'

				except Exception, e:
					print e
					return 'Error'

		except:
			print 'Download Timeout Error...'
			self.link_text = self.text
			return 'Error'


	#Detect is a string all ascii
	def is_all_ascii(self, s):
    		return all(ord(c) < 128 for c in s)

    #Detect is this tweet a English tweet
	def isEnglish(self):
		
		s = self.raw
		clean_s = self.text

		#too short
		if len(clean_s) < 20:
			return False

		#remove non-ascii char
		#can tolerate some emoji or special symbol (the Threshold is 0.8)
		
		if float(len(clean_s))/float(len(s)) < 0.8:
			return False


		#langdetect
		try:
			if langdetect.detect(clean_s) != u'en':
				return False
		except Exception, e:
			return False
		

		#detect stopwords
		'''
		language_ratios = {}

		tokens = nltk.wordpunct_tokenize(clean_s)
		words = [word.lower() for word in tokens]

		for language in stopwords.fileids():
			stopwords_set = set(stopwords.words(language))
			words_set = set(words)
			common_elements = words_set.intersection(stopwords_set)

			language_ratios[language] = len(common_elements)

		most_rated_language = max(language_ratios, key = language_ratios.get)
		most_rated_score = language_ratios[most_rated_language]
		if most_rated_language != 'english' or most_rated_score == 0:
			return False
		'''

		return True

	def isRT(self):
		if self.text[0:4] == 'RT @':
			return True
		else:
			return False

	def hasUrl(self):
		if 'http://' in self.text or 'https://' in self.text:
			return True
		else:
			return False

	def urlCount(self):
		return self.text.count('http')

	def hasHashtag(self):
		if '#' in self.text:
			return True
		else:
			return False

	def toAscii(self):
		self.text = self.text.encode('ascii', 'ignore')
		return self

	def hashtagCount(self):
		return self.text.count('#')

	def remove_hyperlink(self):
		self.text = re.sub(r'http\S+', '', self.text)
		return self
	
	def remove_punctuation(self):
		self.toAscii()
		self.text = self.text.replace('-', ' ')
		self.text = self.text.translate(None, string.punctuation)
		return self

	def remove_username(self):
		self.text = re.sub(r'@[^\s]+', '', self.text)
		return self

	def stem(self):
		if self.stemmed != []:
			return self.stemmed
		stemmer = SnowballStemmer("english")
		self.remove_username().remove_hyperlink()
		wordlist = []
		for sentence in nltk.sent_tokenize(self.remove_punctuation().text):
			for word in nltk.word_tokenize(sentence):
				stemmed = stemmer.stem(word)
				if stemmed.isalpha() and stemmed != 'rt':
					wordlist.append(stemmed)
		self.stemmed = wordlist
		return wordlist

	def stem_text(self):
		if self.stemmed != []:
			return self.stemmed
		stemmer = SnowballStemmer("english")

		wordlist = []
		self.clean_text = self.clean_text.encode('ascii', 'ignore')
		self.clean_text = self.clean_text.replace('-', ' ')
		self.clean_text = self.clean_text.translate(None, string.punctuation)

		for sentence in nltk.sent_tokenize(self.clean_text):
			for word in nltk.word_tokenize(sentence):
				stemmed = stemmer.stem(word)
				if stemmed.isalpha():
					wordlist.append(stemmed)
					
		self.stemmed = wordlist
		return wordlist

if __name__ == '__main__':
	from config import PROJ_PATH
	import json


	data_path = PROJ_PATH + '/data/a_status.json'
	indata = open(data_path, 'rb').read()

	data = json.loads(indata)
	t = Tweet()
	t.load(data)
	print t





































