from __future__ import division
import nltk
import re
import string
import urllib2
import urllib
import unicodedata
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from simhash import Simhash
from langdetect import detect

class Tweet:
	'This class is for storage of Tweet data'

	def __init__(self, text=None, id=None, timestamp=None, retweet_count=None, \
				user_friends_count=None, user_followers_count=None, \
				user_statuses_count=None, topicid = None):
		self.id = id
		self.timestamp = timestamp
		self.text = text
		self.retweet_count = retweet_count
		self.user_friends_count = user_friends_count
		self.user_followers_count = user_followers_count
		self.user_statuses_count = user_statuses_count
		self.topicid = topicid
		self.link_text = ''

		self.stemmed = []

	def __str__(self):
		return self.text

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

		wordlistA = TweetA.stem()
		wordlistB = TweetB.stem()

		intScore = 0
		uniScore = 0
		for word in wordlistA:
			intScore += len(word)
		for word in wordlistB:
			intScore += len(word)

		for word in wordlistA:
			if word in wordlistB:
				uniScore += 2 * len(word)
				wordlistB.remove(word)

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
		text = self.text
		try:
			if 'https' in text:
				url = text[text.find('http'):text.find('http')+23].encode('ascii', 'ignore')
			elif 'http' in text:
				url = text[text.find('http'):text.find('http')+22].encode('ascii', 'ignore')
			else:
				self.link_text = self.text
				return False

			print url
			request = urllib2.Request(url)
			response = urllib2.urlopen(request, timeout = 3)
			html = response.read()
			clean_html = re.sub(r'<.*?>', '', html)
			print clean_html
			self.link_text = clean_html
			return True

		except Exception as ex:
			print str(ex)
			self.link_text = self.text
			return False


	#Detect is a string all ascii
	def is_all_ascii(self, s):
    		return all(ord(c) < 128 for c in s)

    #Detect is this tweet a English tweet
	def isEnglish(self):
		
		s = self.text
		#remove non-ascii char
		#can tolerate some emoji or special symbol (the Threshold is 0.8)
		clean_s = s.encode('ascii','ignore')
		if float(len(clean_s))/float(len(s)) < 0.8:
			return False


		#langdetect
		if detect(s) != u'en':
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






































