import json
from datetime import datetime
import requests

PATH = './push/'

base_url = 'http://54.164.151.19/tweet/'
client_id = '8gLfO50QLnSV'
#url = 'http://54.164.151.19/tweet/MB245/738418531520352258/8gLfO50QLnSV'
headers = {'Content-Type': 'application/json'}

class A_push():

	def __init__(self):
		self.last_access_day = str(datetime.utcnow())[8:10]
		self.topid_push_count = {}
		f = open('TREC2016-MB-testtopics-150.txt')
		tops = json.loads(f.read())
		f.close()
		for top in tops:
			self.topid_push_count[top['topid']] = 0

	def reset_topid_push_count(self):
		self.topid_push_count = {}
		f = open('TREC2016-MB-testtopics-150.txt')
		tops = json.loads(f.read())
		f.close()
		for top in tops:
			self.topid_push_count[top['topid']] = 0

	def a_push_ok(self, tweet_id, relevant_topid, relevant_score):
		if str(datetime.utcnow())[8:10] != self.last_access_day:
			self.last_access_day = str(datetime.utcnow())[8:10]
			self.reset_topid_push_count()

		if (self.topid_push_count[relevant_topid] + 1 <= 10) and (relevant_score > 0.7):
			return True
		else:
			return False

	def a_push(self, tweet_id, relevant_topid):

		self.topid_push_count[relevant_topid] += 1
		url = base_url + relevant_topid + '/' + str(tweet_id) + '/' + client_id
		response = requests.post(url, headers=headers)
		return response.status_code, response.text

if __name__ == '__main__':
	a_push = A_push()
	print a_push.topid_push_count
	for i in range(20):
		print '********', i+1, '********'
		print a_push.a_push_ok(738418531520352258, 'MB331', 0.9)
		if a_push.a_push_ok(738418531520352258, 'MB331', 0.9):
			print a_push.a_push(738418531520352258, 'MB331')
		print a_push.topid_push_count['MB331']
	a_push.reset_topid_push_count()
	print 
	print a_push.topid_push_count['MB331']
