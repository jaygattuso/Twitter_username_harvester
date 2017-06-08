import json
from pprint import pprint


def process_tweet(tweet):
	""" add your code here...."""
	pprint(tweet)
	print 
	print tweet.keys() 


### set this to a path to some tweet json 
f = r"..\stream_grabs_testing\BeeFaerie\json\01-06-2017_06-51-48_BeeFaerie.json"

### set this to limit the number of tweets you want to work through 
### if no limt, set to False e.g.:
# limit = False
limit  = 2

# opens the file, turns it into JSON
with open(f) as data:
	tweets = json.loads(data.read())

# sets up the limits bounds for the iterator... 
if not limit:
	range_limits = len(tweets)
else:
	range_limits = limit

# Works through the tweets one by one until the limits value is reached
for i, tweet in enumerate(tweets[0:range_limits]):
	process_tweet(tweet)
	# prints a delimiter show boundary between tweets.
	if i+1 != range_limits:
		print "\n ################## Next tweet ##################\n"
	