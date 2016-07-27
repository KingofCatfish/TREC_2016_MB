import json
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
from gensim.models import Word2Vec
import math
from random import shuffle
import pickle


PATH = './relevance/'

class Relevance_estimate():
	def __init__(self):
		f = open(PATH+'profile_terms_203_stem.txt')
		self.profile_terms = json.loads(f.read())
		f.close()

		self.stemmer = SnowballStemmer("english", ignore_stopwords=True)

		self.model = Word2Vec.load_word2vec_format(PATH+'GoogleNews-vectors-negative300.bin', binary=True)
		print self.model.similarity('initial', 'initialize')

		self.tokenizer = RegexpTokenizer(r'\w+')

		f = open(PATH+'svm_clf_l.pkls')
		self.clf_l = pickle.loads(f.read())
		f.close()

		f = open(PATH+'svm_clf_nl.pkls')
		self.clf_nl = pickle.loads(f.read())
		f.close()



	def feature_extractor(self, tweet_data, a_topic_terms):
		tweet = tweet_data
		topic = a_topic_terms

		text_tokens_lower_stem = tweet['text_tokens_lower_stem']
		external_tokens_lower_stem = tweet['external_tokens_lower_stem']

		hits = [] #in order to calculate info
		#calculate ti
		count_ti = 0
		for term in topic['title']:
			if term in text_tokens_lower_stem:
				hits.append(term)
				count_ti += 1

		#calculate te
		count_te = 0
		for term in topic['title']:
			if term in external_tokens_lower_stem:
				hits.append(term)
				count_te +=1

		#calculate di
		count_di = 0
		for term in topic['desc_narr']:
			if term in text_tokens_lower_stem:
				hits.append(term)
				count_di += 1

		#calculate de
		count_de = 0
		for term in topic['desc_narr']:
			if term in external_tokens_lower_stem:
				hits.append(term)
				count_de += 1

		#calculate ei
		count_ei = 0
		for term in topic['expasion']:
			if term in text_tokens_lower_stem:
				hits.append(term)
				count_ei += 1

		#calculate ee
		count_ee = 0
		for term in topic['expasion']:
			if term in external_tokens_lower_stem:
				hits.append(term)
				count_ee += 1

		#calculate is_link
		if tweet['isLink'] == True:
			is_link = 1
		else:
			is_link = 0

		#calculate log_followers_count
		log_followers_count = math.log(tweet['followers_count']+1)

		#calculate log_statuses_count
		log_statuses_count = math.log(tweet['statuses_count']+1)

		#calculate log_retweet_count
		#log_retweet_count = math.log(tweet.retweet_count+1)

		#calculate world_count
		world_count = len(text_tokens_lower_stem)

		#calculate hashtag_count
		'''
		hashtag special case: CalifornialDrought
		'''
		hashtag_count = 0
		for c in tweet['text']:
			if c == '#':
				hashtag_count += 1

		#calculate info
		hits = list(set(hits))
		hits = [hit for hit in hits if hit in self.model]
		
		if len(hits) == 0:
			info = 0
		else:
			infos = []
			for i in range(10):
				shuffle(hits)
				inline = []
				inline.append(hits[0])
				info = 1
				for hit in hits[1:]:
					info += 1 - max([self.model.similarity(hit, term) for term in inline])
					inline.append(hit)
				infos.append(info)
			info = sum(infos)/float(len(infos))


		#print count_ti, count_te, count_di, count_de, count_ei, count_ee, \
			#is_link, log_followers_count, log_statuses_count, world_count, hashtag_count, info
		return [count_ti, count_te, count_di, count_de, count_ei, count_ee, \
			is_link, log_followers_count, log_statuses_count, world_count, hashtag_count, info]


	def sniper_estimate(self, tweet, candidate_topid):
		tweet_data = {}
		tweet_data['text'] = tweet.text.encode('ascii','ignore')
		tweet_data['link_text'] = tweet.link_text.encode('ascii','ignore')
		tweet_data['isLink'] = tweet.isLink
		tweet_data['followers_count'] = tweet.followers_count
		tweet_data['statuses_count'] = tweet.statuses_count
		tweet_data['id'] = tweet.id

		
		text_tokens = self.tokenizer.tokenize(tweet_data['text'])
		text_tokens_lower_stem = set([self.stemmer.stem(token.lower()) for token in text_tokens])
		external_tokens = self.tokenizer.tokenize(tweet_data['link_text'])
		external_tokens_lower_stem = set([self.stemmer.stem(token.lower()) for token in external_tokens])

		tweet_data['text_tokens_lower_stem'] = text_tokens_lower_stem
		tweet_data['external_tokens_lower_stem'] = external_tokens_lower_stem

		for a_topic_terms in self.profile_terms:
			if a_topic_terms['topid'] == candidate_topid:
				the_topic_terms = a_topic_terms
				break
				
		samples = []

		feature_vec = self.feature_extractor(tweet_data, the_topic_terms)
		samples.append(feature_vec)

		if tweet_data['isLink']:
			predict_probas = self.clf_l.predict_proba(samples)
		elif not tweet_data['isLink']:
			predict_probas = self.clf_nl.predict_proba(samples)

		return candidate_topid, predict_probas[0][2]



	def estimate(self, tweet):
		tweet_data = {}
		tweet_data['text'] = tweet.text.encode('ascii','ignore')
		tweet_data['link_text'] = tweet.link_text.encode('ascii','ignore')
		tweet_data['isLink'] = tweet.isLink
		tweet_data['followers_count'] = tweet.followers_count
		tweet_data['statuses_count'] = tweet.statuses_count
		tweet_data['id'] = tweet.id

		
		text_tokens = self.tokenizer.tokenize(tweet_data['text'])
		text_tokens_lower_stem = set([self.stemmer.stem(token.lower()) for token in text_tokens])
		external_tokens = self.tokenizer.tokenize(tweet_data['link_text'])
		external_tokens_lower_stem = set([self.stemmer.stem(token.lower()) for token in external_tokens])

		tweet_data['text_tokens_lower_stem'] = text_tokens_lower_stem
		tweet_data['external_tokens_lower_stem'] = external_tokens_lower_stem

		samples = []

		for a_topic_terms in self.profile_terms:
			#print a_topic_terms['topid']
			"""
				a_topic_terms = { (all stemed !!!)
					"title": ["PA", "Hershey", "quilt", "show"], 
					"desc_narr": ["lodging", "Tweets", "quilts", "prize", "quilter", "logistics", "teachers", "vendors", "opinions", "winning"], 
					"expasion": ["Odyssey", "2016", "Lodge", "quilting", "Shows", "Quilting", "Convention",  "Quilters", "quiltodyssey", "Pennsylvania", "17033", "Extravaganza", "Hours", "Quilter", "AQS", "Center", "quilts", "guilds", "5148", "10am"], 
					"topid": "MB226"
					}

			"""
			is_possible = False
			for term in a_topic_terms['title']:
				if term in text_tokens_lower_stem:
					is_possible = True
					break

			if is_possible:
				feature_vec = self.feature_extractor(tweet_data, a_topic_terms)
			else:
				feature_vec = [0,0,0,0,0,0,0,0,0,0,0,0]

			samples.append(feature_vec)

		if tweet_data['isLink']:
			predict_probas = self.clf_l.predict_proba(samples)
		elif not tweet_data['isLink']:
			predict_probas = self.clf_nl.predict_proba(samples)

		proba_topid_pairs = [(predict_probas[i], self.profile_terms[i]['topid'], self.profile_terms[i]['title']) for i in range(len(self.profile_terms))]
		max_proba_topid_pair= max(proba_topid_pairs, key=lambda t:t[0][2])

		relevant_topid, relevant_score, relevant_title = max_proba_topid_pair[1], max_proba_topid_pair[0][2], max_proba_topid_pair[2]
		return relevant_topid, relevant_score, relevant_title

if __name__ == '__main__':
	re = Relevance_estimate()
	import pickle
	f = open('result_0.pkl','rb')
	status0= pickle.load(f)
	f.close()

	from Tweet import Tweet
	f = open('test0.txt','w')
	for s in status0:
		print >>f, '###########################################'
		print >>f, '###########################################'
		print >>f, '###########################################'
		print >>f, s[0]
		tweet = Tweet()
		tweet.load_tweepy(s[1])
		print >>f, tweet.text
		if tweet.crawl_link_text() == 'Error':
			continue
		print >>f, re.estimate(tweet)
	f.close()



			