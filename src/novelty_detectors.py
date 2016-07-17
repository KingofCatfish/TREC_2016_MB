import novelty_detection as nd
import Tweet
import pickle
from config import NOVELTY_DETECTION_RECOVERY_FILE 

class novelty_detectors:
	'''
		Usage:

		detector = novelty_detectors()
		detector.novelty_detect(tweet, topic_id)
	'''
	def __init__(self):
		self.topic_map = {}
		self.reload()

	def novelty_detect(self, tweet, topic_id):
		if topic_id not in self.topic_map.keys():
			self.topic_map[topic_id] = nd.novelty_detection('naive', 'production', topicid = topic_id)
			self.topic_map[topic_id].config(naive_valve = 0.68)
			self.backup()

		return self.topic_map[topic_id].stream(tweet)

	def reload(self):
		try:
			recovery_file = open(NOVELTY_DETECTION_RECOVERY_FILE , 'rb')
			t_keys = pickle.load(recovery_file)
			for k in t_keys:
				self.topic_map[k] = nd.novelty_detection('naive', 'production', topicid = k)
				self.topic_map[k].config(naive_valve = 0.68)
			recovery_file.close()
		except IOError:
			recovery_file = open(NOVELTY_DETECTION_RECOVERY_FILE, 'wb')
			recovery_file.close()

	def backup(self):
		recovery_file = open(NOVELTY_DETECTION_RECOVERY_FILE, 'wb')
		pickle.dump(self.topic_map.keys(), recovery_file)
		recovery_file.close()

if __name__ == '__main__':
	#for testing

	a = Tweet.Tweet(text = 'abc')
	b = Tweet.Tweet(text = 'cdf')

	detector = novelty_detectors()
	print detector.novelty_detect(a, 1)
	print detector.novelty_detect(a, 2)
	print detector.novelty_detect(a, 3)