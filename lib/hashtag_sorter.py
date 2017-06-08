import os
import operator
from dateutil import parser
from datetime import datetime, timedelta


def get_sorted_hashtag_counts(base_out_folder, days_delta=0):
	""" Takes a log of all hashtags, and makes freq graph sorted by most common
	timedelta is used to make different time window views of hashtags
	defaults to 0 time delta
	Is using key of tweet_id+hashtag because one tweet can have more than one hashtag
	"""
	hashtags_dict = {}
	counted_tweets = []
	with open(os.path.join(base_out_folder, "####logs", "hashtags.txt")) as data:
		lines = data.read().split("\n")
		for line in lines[1:-1]:
			tweeter, tweet_date, tweet_id, crawl_time, hashtag = line.split("|")
			key = tweet_id+hashtag
			tweet_date = datetime.strptime(tweet_date, "%Y-%m-%d %H:%M:%S")

			if days_delta == 0:
				### check each hashtag in the tweet - add if not counted
				if key not in counted_tweets:
					counted_tweets.append(key)
					if hashtag not in hashtags_dict:
						hashtags_dict[hashtag] = 0
					hashtags_dict[hashtag] += 1
			else:
				stopdate = datetime.today() - timedelta(hours=days_delta*24)
				if tweet_date > stopdate:
					### check each hashtag in the tweet - add if not counted
					if key not in counted_tweets:
						counted_tweets.append(key)
						if hashtag not in hashtags_dict:
							hashtags_dict[hashtag] = 0
						hashtags_dict[hashtag] += 1

	sorted_hashtags = sorted(hashtags_dict.items(), key=operator.itemgetter(1), reverse=True)
	return sorted_hashtags

def main():
	pass

if __name__ == '__main__':
	main()