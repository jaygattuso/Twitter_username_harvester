import requests
import shutil
import os

base_out_folder = "stream_grabs"

def get_file(url, file_path):
	response = requests.get(url, stream=True)
	with open(file_path, 'wb') as out_file:	
		shutil.copyfileobj(response.raw, out_file)
	del response

def get_media():
	with open(os.path.join(base_out_folder, "####logs", "media_log.txt")) as data: 
		lines = data.read().split("\n")
		for line in lines[1:-1]:
			name, tweet_date, tweet_id, crawl_date, url = line.split("|") 
			__, file_name = url.rsplit("/", 1) 
			file_path = os.path.join(base_out_folder, name, "assets", file_name)
			if not os.path.exists(file_path):
				print "{}: {}".format(name, url)
				get_file(url, file_path)

def main():
	pass

if __name__ == '__main__':
	main()