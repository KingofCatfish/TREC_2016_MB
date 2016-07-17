from __future__ import division
from Tweet import Tweet
from Tweets import Tweets
import pickle
import json
import random
import math
from config import NOVELTY_DETECTION_RECOVERY_DIR 
from config import PROJ_PATH

class novelty_detection:
	'''
		This class is for novelty detection.

		Sample Usage:

		import novelty_detection as nd

		detector = nd.novelty_detection('naive', 'production')
		detector.config(naive_valve = 0.6)

		for t in tweets:
			if detector.stream(t):
				report(t)
	'''

	method_list = {
		'naive' : {
			'method_name' : 'naive similarity detection',
			'parameter' : {
				'naive_valve' : 0.6
			},
			'callback_name' : 'naive_stream'
		},
		'simhash' : {
			'method_name' : 'Simhash similarity detection',
			'parameter' : {
				'simhash_valve' : 90
			},
			'callback_name' : 'simhash_stream'
		},
		'plain' : {
			'method_name' : 'plain detection',
			'parameter' : {},
			'callback_name' : 'plain_stream'
		},
		'sample method' : {
			'method_name' : 'just a sample method',
			'parameter' : {
				'parameter1' : 1,
				'parameter2' : 2
			},
			'callback_name' : 'sample_stream'
		}
	}
	
	def __init__(self, method, environment = 'debug', topicid = None):
		if method in novelty_detection.method_list:
			self.method = novelty_detection.method_list[method]['method_name']
			self.reported = []
			self.parameter = novelty_detection.method_list[method]['parameter']
			self.stream_callback = getattr(self, novelty_detection.method_list[method]['callback_name'])
			self.topicid = topicid
			if environment != 'debug':
				self.environment = 'production'
				if topicid == None:
					raise Exception('must specify topic id')
			else:
				self.environment = 'debug'
			self.reload()
		else:
			raise Exception('novelty_detection does not support ' + str(method))

	def __str__(self):
		return 'Novelty Detector with ' + self.method

	def reload(self):
		if self.environment == 'debug':
			return
		try:
			recovery_file = open(NOVELTY_DETECTION_RECOVERY_DIR + str(self.topicid) + '.tmp', 'rb')
			self.reported = pickle.load(recovery_file)
			recovery_file.close()
		except IOError:
			recovery_file = open(NOVELTY_DETECTION_RECOVERY_DIR + str(self.topicid) + '.tmp', 'wb')
			recovery_file.close()

	def backup(self):
		recovery_file = open(NOVELTY_DETECTION_RECOVERY_DIR + str(self.topicid) + '.tmp', 'wb')
		pickle.dump(self.reported, recovery_file)
		recovery_file.close()


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

		ret = self.stream_callback(tweet)
		if ret:
			self.reported.append([tweet])
			if self.environment == 'production':
				self.backup()
		return ret

	def naive_stream(self, tweet):
		for doc in self.reported:
			if doc[0].naive_similarity(tweet, doc[0]) > self.parameter['naive_valve']:
				doc.append(tweet)
				return False
		
		return True

	def simhash_stream(self, tweet):
		for doc in self.reported:
			if doc[0].simhash_similarity(tweet, doc[0]) > self.parameter['simhash_valve']:
				doc.append(tweet)
				return False

		return True

	def plain_stream(self, tweet):
		return True

	#TODO
	def auto_tuning(self, Tweets):
		pass

def print_tweets_collection(tweets):
	text = []
	for cluster in tweets:
		t = []
		for tweet in cluster:
			t.append(tweet.text)
		text.append(t)
	print json.dumps(text, indent = 4)

def accuracy_test(resultA, resultB, round = 10000):
	mapA = {}
	mapB = {}
	id_list = []

	label = 0
	for cluster in resultA:
		label += 1
		for tweet in cluster:
			mapA[tweet.id] = label
			id_list.append(tweet.id)

	if id_list == []:
		return None, 0

	label = 0
	for cluster in resultB:
		label += 1
		for tweet in cluster:
			mapB[tweet.id] = label

	length = len(mapA)
	label_set = [(random.choice(id_list), random.choice(id_list)) for item in range(round)]

	match = 0
	for tweetA, tweetB in label_set:
		if tweetA == tweetB:
			round -= 1
			continue
		if (mapA[tweetA] == mapA[tweetB] and mapB[tweetA] == mapB[tweetB]) or (mapA[tweetA] != mapA[tweetB] and mapB[tweetA] != mapB[tweetB]) :
			match += 1
	if match == 0:
		return 0, length
	else:
		return match / round, length

def nmi_test(result, standard):

	label = 0
	standard_dict = {}
	standard_freq = []
	for cluster in standard:
		for tweet in cluster:
			standard_dict[tweet.id] = label
		label += 1	
		standard_freq.append(len(cluster))

	N = sum(standard_freq)
	if N == 0:
		return None, 0

	result_freq = []
	union_table = []
	for cluster in result:
		result_freq.append(len(cluster))
		union_row = [0] * len(standard_freq)
		for tweet in cluster:
			union_row[standard_dict[tweet.id]] += 1
		union_table.append(union_row)

	nmi = 0
	for r_cluster in range(len(result_freq)):
		for s_cluster in range(len(standard_freq)):
			if union_table[r_cluster][s_cluster] == 0:
				continue
			temp = union_table[r_cluster][s_cluster] * N
			temp /= standard_freq[s_cluster] * result_freq[r_cluster]
			temp = math.log(temp)
			temp *= union_table[r_cluster][s_cluster] / N
			nmi += temp

	nmi_r = 0
	nmi_s = 0

	for r_cluster in range(len(result_freq)):
		temp = result_freq[r_cluster] / N
		nmi_r -= temp * math.log(temp)

	for s_cluster in range(len(standard_freq)):
		temp = standard_freq[s_cluster] / N
		nmi_s -= temp * math.log(temp)

	if nmi_r + nmi_s == 0:
		return 1, N

	return (2 * nmi) / (nmi_r + nmi_s), N



if __name__ == '__main__':
	NOVELTY_DATA_PREP_FILE = PROJ_PATH + '/tmp/novelty_data_prep.pkl'
	recovery_file = open(NOVELTY_DATA_PREP_FILE, 'rb')
	train_data = pickle.load(recovery_file)['train']

	train = {}
	for item in train_data:
		train[item.id] = item

	standard_file = open(PROJ_PATH + '/data/past_training_data/TREC 2015 Microblog Track/clusters-2015.json', 'r').read()
	st_data = json.loads(standard_file)

	parameter = []
	high_score = 0
	high_valve = 0
	for valve in range(1, 1000):
		count = 0
		score = 0
		for topic in st_data['topics']:
			nd = novelty_detection('plain', 'debug')
			#nd.config(naive_valve = valve / 1000)simhash_valve

			st_reported = []

			for tweets in st_data['topics'][topic]['clusters']:
				st_tweets = []
				for tweet in tweets:
					try:
						st_tweets.append(train[int(tweet)])
						if nd.stream(train[int(tweet)]):
							pass
							#print train[int(tweet)]
					except KeyError:
						pass
				if st_tweets != []:
					st_reported.append(st_tweets)


			print topic + ' ',
			[rate, num] = nmi_test(nd.reported, st_reported)
			print rate, num
			if num != 0:
				score += rate * num
				count += num



			#break
		print 'Final Score(' + str(valve / 1000) + '): ' + str(score / count)
		if score / count > high_score:
			high_score = score / count
			high_valve = valve
		parameter.append([valve / 1000, score / count])
		break

	print '**** Best valve: ' + str(high_valve) + '  with score ' + str(high_score) 
	para_file = open('parameter.json', 'w')
	para_file.write(json.dumps(parameter))
	para_file.close()
	# print train[622931017213440000].stem()
	# print train[622954249488502784].stem()
	# print train[623029751125401600].stem()
	# print train[623166258951774208].stem()
	# print train[623175855536254976].stem()
	# print train[623439631128920064].stem()
	# print train[623495096588054529].stem()
	# print train[623559323961163776].stem()
	# print train[623649925109317632].stem()












	