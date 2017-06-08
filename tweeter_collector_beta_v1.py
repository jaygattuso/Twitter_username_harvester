import os
import time
import json
import pytz
import dateutil.rrule
import dateutil.parser
import operator
import lib.asset_collector as asset_collector
import lib.hashtag_sorter as hashtag_sorter
from lib.twarc import Twarc 
from pprint import pprint, pformat
from email.utils import parsedate_tz
from datetime import datetime, timedelta

#####################  dates setup ######################
####   http://journal.code4lib.org/articles/11358    ####
####   http://stackoverflow.com/questions/4695609/checking-date-against-date-range-in-python
####   http://stackoverflow.com/questions/3743222/how-do-i-convert-datetime-to-date-in-python 
timezone = pytz.timezone('Pacific/Auckland')
# this is not currently used. 
# start_date = timezone.localize(dateutil.parser.parse("01-May-2016"))
start_date = datetime.now(timezone)
# sets the end date for the crawler 
end_date = timezone.localize(dateutil.parser.parse("31-Oct-2017"))
#########################################################

######################   twitter setup   ##############################
# add your credentials here
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)
#######################################################################

######################### in/out vars setting  ########################
""" base_out_folder doesn't need to exist.
names_file needs to exist, new line seperated tweeter names or profile urls
optional - per tweeter, comma seperate tweeter id and the tweet id you 
want to start harvesting from"""

base_out_folder = "stream_grabs"
names_file = "example_names.txt"
########################################################################

###### set up the files and folders for the crawl #####################
hashtags_log = "hashtags.txt"
urls_log = r"urls_file.txt"
media_log = r"media_log.txt"
seen_tweets = r"seen_tweets.txt"

logs_folder = os.path.join(base_out_folder, "####logs")
if not os.path.exists(logs_folder):
	os.makedirs(logs_folder)
harvest_data_indexes = os.path.join(base_out_folder, "####harvest_data_indexes")
if not os.path.exists(harvest_data_indexes):
	os.mkdir(harvest_data_indexes )

master_hashtags_log_path = os.path.join(logs_folder, hashtags_log)
master_urls_log_path = os.path.join(logs_folder, urls_log)
master_media_log_path = os.path.join(logs_folder, media_log)
master_seen_tweets_path = os.path.join(logs_folder, seen_tweets)

for item in [master_hashtags_log_path, master_urls_log_path, master_media_log_path, master_seen_tweets_path]:
	if not os.path.exists(item):
		open(item, 'wb').close()
		if item == master_hashtags_log_path:
			with open(item, "w") as data:
				data.write("tweeter|tweet_date|tweet_ID|crawl_time|hashtag\n")
		if item == master_urls_log_path:
			with open(item, "w") as data:
				data.write("tweeter|tweet_date|tweet_ID|crawl_time|url|expanded_url|display_url\n")
		if item == master_media_log_path:
			with open(item, "w") as data:
				data.write("tweeter|tweet_date|tweet_ID|crawl_time|media_url\n")
		if item == master_seen_tweets_path:
			with open(item, "w") as data:
				data.write("tweeter|tweet_date|tweet_ID|crawl_time\n")
#######################################################################

def tweet_date_to_datetime(datestring):
	"""converts the datetime string in the tweet into a datetime object"""
	time_tuple = parsedate_tz(datestring.strip())
	dt = datetime(*time_tuple[:6])
	return dt - timedelta(seconds=time_tuple[-1])

def extract_hashtags(tweet):
	""" if hashtags in file returns text of hashtags"""
	hashtags = []
	if tweet["entities"]["hashtags"] == []:
		return []
	else:
		for tag in tweet["entities"]["hashtags"]:
			hashtags.append(tag["text"])
	for hashtag in hashtags:
		hashtag = hashtag.encode("utf-8", "ignore")
		line = "{}|{}|{}|{}|{}\n".format(name,
									tweet_date,
									tweet_id,
									crawl_time,
									hashtag)
		append_line_to_log(hashtags_log_path, line)
		append_line_to_log(master_hashtags_log_path, line)

def extract_urls(tweet):
	"""if url in tweet returns the url strings for logging:
	tweeter, date of tweet, url, full url, displayed url"""
	for item in tweet["entities"]["urls"]:
		line = "{}|{}|{}|{}|{}|{}|{}\n".format(name,
									tweet_date,
									tweet_id,
									crawl_time,
									item["url"].encode("utf-8", "ignore"), 
									item["expanded_url"].encode("utf-8", "ignore"), 
									item["display_url"].encode("utf-8", "ignore"))
		append_line_to_log(urls_log_path, line)
		append_line_to_log(master_urls_log_path, line)


def make_tweeter_folders(tweeter):
	""" for each tweeter, sets up their own space for the crawl assets (
	folders and log files etc)"""
	hashtags_log = "hashtags.txt"
	urls_log = r"urls_file.txt"
	media_log = r"media_log.txt"
	seen_tweets = r"seen_tweets.txt"

	logs_folder = os.path.join(base_out_folder, tweeter, "logs")
	if not os.path.exists(logs_folder):
		os.makedirs(logs_folder)
	assets_folder = os.path.join(base_out_folder, tweeter, "assets")
	if not os.path.exists(assets_folder):
		os.makedirs(assets_folder)
	json_folder = os.path.join(base_out_folder, tweeter, "json")
	if not os.path.exists(json_folder):
		os.makedirs(json_folder)

	hashtags_log_path = os.path.join(logs_folder, hashtags_log)
	urls_log_path = os.path.join(logs_folder, urls_log)
	media_log_path = os.path.join(logs_folder, media_log)
	seen_tweets_path = os.path.join(logs_folder, seen_tweets)

	for item in [hashtags_log_path, urls_log_path, media_log_path, seen_tweets_path]:
		if not os.path.exists(item):
			open(item, 'wb').close()
			if item == hashtags_log_path:
				with open(item, "w") as data:
					data.write("tweeter|tweet_date|tweet_id|crawl_date|hashtag\n")
			if item == urls_log_path:
				with open(item, "w") as data:
					data.write("tweeter|tweet_date|tweet_id|crawl_date|url|expanded_url|display_url\n")
			if item == media_log_path:
				with open(item, "w") as data:
					data.write("tweeter|tweet_date|tweet_id|crawl_date|media_url\n")
			if item == seen_tweets_path:
				with open(item, "w") as data:
					data.write("tweeter|tweet_date|tweet_id|crawl_date\n")
	return hashtags_log_path, urls_log_path, media_log_path, seen_tweets_path, json_folder, assets_folder

def extract_media(tweet):
	"""if media in tweet returns the url strings for logging:
	tweeter, date of tweet, url of media"""
	if "media" in tweet["entities"]:
		seen_media = []
		for item in tweet["extended_entities"]["media"]:
			for_collecting = False
			content_url = item["url"] 
			if content_url in seen_media:
				pass
			else:
				if item["type"] == "photo" or item["type"] == "animated_gif":
					seen_media.append(content_url)
					download_url = item["media_url"]
					for_collecting = True
				elif item["type"] == "video":
					for i, varient in enumerate(item["video_info"]["variants"]):
						if varient["content_type"] == "video/mp4" and not for_collecting:
							download_url = varient["url"]
							seen_media.append(content_url)
							for_collecting = True
				else:
					print "Unknown media type..", tweet["tweet_id"]
					download_url = item["media_url"]
			if for_collecting:
				line = "{}|{}|{}|{}|{}\n".format(name, tweet_date, tweet_id,	crawl_time,	download_url)
				append_line_to_log(media_log_path, line)
				append_line_to_log(master_media_log_path, line)
			
def make_html_page():
	""" updates the html index page so basic crawl stats can be seen in a browser"""
	number_of_tweeters = len(names)
	unique_tweets = []
	times_run = []
	with open(master_seen_tweets_path) as data:
		lines = data.read().split("\n")
		for line in lines[1:-1]:
			tweeter, tweet_date, tweet_id, crawl_time = line.split("|")
			if tweet_id not in unique_tweets:
				unique_tweets.append(tweet_id)
			if crawl_time not in times_run:
				times_run.append(crawl_time)
	try:
		os.rename("harvest_data.html", os.path.join(harvest_data_indexes, "harvest_data_{}.html".format(crawl_time)))	
	except:
		pass		
	
	last_crawl_date, last_crawl_time =  crawl_time.replace("-", "/", 2).replace("-", ":", 2).split("_")
	with open(os.path.join("lib", "template.html")) as infile:
		template = infile.read()
		template = template.replace("LAST_RUN", "{} at {}".format(last_crawl_date, last_crawl_time))
		template = template.replace("NUMBER_OF_SEEN_TWEETS", str(len(unique_tweets)))
		template = template.replace("NUMBER_OF_TIMES_RUN", str(len(times_run)))
		template = template.replace("NUMBER_OF_TWEETERS", str(len(names)))
		template = template.replace("TOP_TEN_HASHTAGS", make_hashtags_html())
	with open("harvest_data.html", "wb") as outfile:
		outfile.write(template)

def make_hashtags_html():
	"""works out the top ten hashtags of a given set of terms"""
	text = "<p><table><tr><th>Day</th><th>Week</th><th>All</th></tr>\n"
	for i in range(0,10):
		try:
			day_item = "#{} ({})".format(hashtags_day[i][0], hashtags_day[i][1])
		except:
			day_item = ""
		try:
			week_item = "#{} ({})".format(hashtags_week[i][0], hashtags_week[i][1])
		except:
			week_item = ""
		try:
			all_item = "#{} ({})".format(hashtags_all_time[i][0],hashtags_all_time[i][1])
		except:
			all_item = ""
		text += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>\n".format(day_item, week_item, all_item)
	text += "</table>\n"
	return text

def append_line_to_log(logfile, line):
	""" takes a log file name, and a log line, and appends to file"""
	with open(logfile, "a") as data:
		data.write(line)

#### read in the tweeter usernames to process #### 
"""
new line seperated tweeter names or profile urls
optional - per tweeter, comma seperate tweeter id and the tweet id you 
want to start harvesting from
No headers. 
"""
with open(names_file) as data:
	data = data.read()
	names = data.split("\n")
##################################################

################ Start main process ##################
""" rolls from start date until end date.
Watch out for timeouts /twitters naughty corner. Twarc will try and stop twitter from blocking you, 
but I've not really tested what happens. 
If your tweeter list is small you might hit twitter too fast. 

consider using a sleep, e.g.:- 

time.sleep(600) 

after the while loop to give a back off. 600 == 600 seconds == 10 mins. 
 """ 
while  start_date < datetime.now(timezone) < end_date:
	# time.sleep(600) 
	crawl_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
	for i, name in enumerate(names):
		### support for a names list that has no "since" column. 
		try:
			name, since_id = name.split(",")
		except:
			since_id = False

		### names list is sometimes given as full tweeter IDs
		name = name.strip().replace("https://twitter.com/", "").replace("?", "")
		### or with a trailing backslash
		if name.endswith('/'):
			name = name[:-1]
		### or a leading @ symbol
		if name.startswith("@"):
			name = name[1:]
		### stands up the tweeter storage parts
		hashtags_log_path, urls_log_path, media_log_path, seen_tweets_path, json_folder, assets_folder = make_tweeter_folders(name)
		print "{} of {}: {}".format(i+1, len(names), name)
		tweets = []
		
		### handles the two differnt input lists. 
		if since_id != "False":
			try:
				timeline_tweets = t.timeline(screen_name=name, since_id=since_id)
			except:
				print "Failed to get timeline, skipping"
				continue
		else:
			try:
				timeline_tweets = t.timeline(screen_name=name)
			except:
				print "Failed to get timeline, skipping"
				continue

		### per tweet set processing 
		for tweet in timeline_tweets:
			tweet_id = tweet["id_str"]
			tweet_date = tweet_date_to_datetime(tweet["created_at"])

			############# per tweet processing ############
			extract_hashtags(tweet)
			extract_urls(tweet)
			extract_media(tweet)
			tweets.append(tweet)
			line = "{}|{}|{}|{}\n".format(name, tweet_date, tweet_id, crawl_time)
			append_line_to_log(seen_tweets_path, line)
			append_line_to_log(master_seen_tweets_path, line)
			###############################################

		############# write out tweeter json file ############################################################
		file_path = '{}_{}.json'.format(os.path.join(json_folder, (time.strftime("%d-%m-%Y_%H-%M-%S"))), name) 
		with open(file_path, "w") as outfile:
			json.dump(tweets, outfile)
		######################################################################################################

	########### post havest tick events ###############
	asset_collector.get_media(base_out_folder)
	hashtags_all_time = hashtag_sorter.get_sorted_hashtag_counts(base_out_folder, days_delta=0)
	hashtags_day = hashtag_sorter.get_sorted_hashtag_counts(base_out_folder, days_delta=1)
	hashtags_week = hashtag_sorter.get_sorted_hashtag_counts(base_out_folder, days_delta=7)
	make_html_page()
	###################################################



### deployment notes
# removed = https://twitter.com/Godfrey_Rudolph - protected. 

