import tweepy
import nltk
import time
import pickle

consumer_key = "a7vdFgIeOzMtv5SEf5Nw7euEy"
consumer_secret = "FUeuYbCK3oatQ2zcUP4st7JvUZeVRCvFtChe9i4YOZgZPFS7k8"
access_token = "2547796078-NukRjzi5dVONtf0H44KXoVwvVWINQ1q2PLCBsea"
access_token_secret = "XIwJdgZsKZ5Dq8NlYsq4h7lrRmjyJJr9rCnC2uQTshGeS"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


fp = open('3_qrels_2015.txt')
lines = fp.readlines()
fp.close()
tokenized_lines = []
for line in lines:
	tokenized_lines.append(nltk.word_tokenize(line))

count = 0
request_list = []

result_list_of_topic_and_status = []
for row, line in enumerate(tokenized_lines):
	print '******', row, '/', len(tokenized_lines), '******'
	request_list.append(line[2])

	count = (count + 1) % 100
	if count == 0:
		#The order of tweet IDs may not match the order of tweets in the returned array.
		status = api.statuses_lookup(request_list)
		for statu in status:
			for i in range(row+1-100,row+1):
				if int(tokenized_lines[i][2]) == statu.id:
					offset = i
					break
			result_list_of_topic_and_status.append((tokenized_lines[offset][0], statu))
		request_list = []
		print 'len(status):', len(status)
		time.sleep(80)


output = open('result_3.pkl', 'wb')
pickle.dump(result_list_of_topic_and_status, output)
output.close()


















