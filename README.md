This guide pertains to tweeter_collector_beta_v1.py
If the version you have is different, things might have changed...

Also, no warrenties - things might break, I've not done much bug squshing...

__________ prerequisites ______________

You need to have set up twarc with twitter API keys/secrets etc

https://github.com/DocNow/twarc\
https://dev.twitter.com/oauth/overview/application-owner-access-tokens
 
________ How to use ______________

It should be mainly self managing. Its not currently set up for looped use. 
It runs once, then stops. It is designed to run contiously, running it again 
is not deleterious or problematic, infact its desirable. 

Before you run the script, there are three things to possibly change.
It will (should) work out-of-the-box, just with the default values 
(assuming there is a valid names file for it to work from - more on this below). 
 

1) on line 43: test = True

I set it up to allow rapid switching between test and "prod" instances. 
There is no difference between the two, it just means you can keep two sets of input 
lists easily accessible, and two different output folders. 

Set to True or False depending on what you want to do. 
(Main usecase is for running debugging testing while a crawl is in flight - 
as a crawl might be many weeks its important to not lose track... )

Associated to this var, set base_out_folder on lines 45 and 49 as 
two locations you want to use. 
They are set to "stream_grabs_testing" and "stream_grabs", 
which will appear in the folder you run the script from at run time. 

You also need to set the names_file on line 46 and 50. 

The names file is just a [new line delimited] list. 
There are two versions that the script can cope with. 

The simplest is a basic list of usernames you want to crawl. 

tweeter_1
tweeter_2
etc. 

If this is the list, the script with grab their entire timeline. 

The second mode accepts two values per line, tweeter username, 
and the tweet ID you want to start harvesting from. The values are comma delimited.

tweeter_1,341224234
tweeter_1,213234235
tweeter_1,934341234
etc. 

The usecase for this is to identify the last tweet from a user, record the ID, 
and only harvest from that tweet. 

There is a helper script in the libs folder that might help you figure out 
what that tweet id is making a new names list.  

Either build and run in an idle (e.g. sublime) 
or from command line run >python tweeter_collector_beta_v1.py

Once its run, it updates the html file harvest_data.html

View this in a browser to get stats about the last time it was run etc. 
This is included instead of a heartbeat. Previous versions of the 
html page are archived. 

__________________ what it does... ________________________

The script consumes the list tweeters and pulls back their timeline. 
If a starting tweet id is given then the timeline is only captured after that ID. 

When initiated for the first time it creates a series of items.  The ####logs folder 
holds the master log files for tweets its seen, media its detected, hashtags its found, 
and urls that have been tweeted. The log files are made, and column headers written. 
The ####archive folder is created, which is where the older harvest_data.html 
files are stored. 

The script then picks up the given names list, and iterates through each given user. 

On the first run it creates a folder for their items, and inside that, 
three more folders: logs, assets, json

The creates the same four log files in the logs folder as the master list in ####logs.

It grabs the timeline and iterates through the tweets. For each tweet it checks for hashtags, 
adding any it finds to the logs (individual and master), same for media - 
adding the url to the binary, and the same for the urls. 
The tweet ID is added to the  seen logs (individual and master)
The tweets are added to a json file, and at the end of the session the json 
file is written to the json folder for that loop. 
The json file is marked with the crawl time. 

Its important to note that this crawl process is highly repetitive. 
Any tweet will be captured repeatedly throughout the crawl. Potentially  
This is by design, and intends to allow the analysis of "momentum" or "trajectory" 
of individual tweets, by inspecting the retweet / favourite count for an individual 
tweet id over time.  

At the end of the names list, the harvest_data.html file is updated, currently showing 
the last run time/date, number of tweeters its following, number of 
unique tweets it has encountered, and lists of the top ten hashtags for the last day, 
week and over the duration of the crawl. 

Finally, the script then loops over the master media log, and attempts to download 
any media it has found. It will not download anything beyond the first encounter, 
the assumption here is that media urls are unique to items, and changes to content 
would result in a new media url. The media content harvester is basic, picking up the 
highest res video / image it can by assuming the position of items in the tweet["media"] 
lists, not inspection... 

Fin. 