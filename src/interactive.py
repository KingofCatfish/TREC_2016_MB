import cmd
import Tweets
import Tweet
from config import TWEET_DATA_PATH

class interactive_helper(cmd.Cmd):
	'''
		This is an interactive testing interface for TREC 2016 MB tarck contest

		Typical usage:

		>>>load 0 		#load result_0.pkl into memory
		>>>peak 3 		#peak the first 3 tweet in memory
		>>>stem 		#remove username, link, punctuation
		>>>peak 5 		#peak the first 5 tweet in memory
		>>>quit 		#quit

	'''
	intro = 'For TREC MB track debugging\nexit/quit/bye to end the session\nhelp to show usage'
	prompt = '>>>'

	def preloop(self):
		self.data = Tweets.Tweets()

	def do_load(self, label = 0):
		'''load pickled data'''
		try:
			self.data.import_from_pickled_data(TWEET_DATA_PATH + 'result_' + label + '.pkl')
		except Exception as e:
			print('invalid loading parameter')
			print(e)
			return False

	def do_stem(self, arg):
		'''Stem text in Tweet Data, sample usage: stem'''
		try:
			self.data.stem()
		except Exception as e:
			print('failed to stem tweet')
			print(e)
			return False

	def do_peak(self, length = 3):
		'''peak into the tweet data, sample usage: peak 3'''
		print('length:' + length)
		print(self.data.peak(int(length)))


	def do_exit(self, arg):
		'''exit from the current session'''
		print('Good Bye')
		return True

	def do_quit(self, arg):
		'''exit from the current session'''
		print('Good Bye')
		return True

	def do_bye(self, arg):
		'''exit from the current session'''
		print('Good Bye')
		return True

if __name__ == '__main__':
	interactive_helper().cmdloop()