import pymongo
from pymongo import MongoClient
from twython import Twython
from twython import TwythonStreamer
import json

app_key="VaHT2vs02najkRK0Gqa6GDSio"
app_secret="0uekE2KNakLyLe3uXAW7IQzBrSlZqSqQY8qlEfOEXzDet2SmKc"
oauth_token="332887810-LfrjaJSxDP7Svz0k9hcCtvNQ3tvqXelTtEnqNdAX"
ouath_token_secret="76yuHM5NKr225Pg33Z3036YQBwvMdyN3fk9WIH0nrIB00"




connection = MongoClient()
db=connection['jnan']

twitter = Twython(app_key,app_secret,oauth_token,ouath_token_secret)

data=twitter.search(q='#SmogFreeCapital',result_type='Mixed',count=100)

statuses = data['statuses']
#print(data['search_metadata'])

while True:	
	if 'next_results' in data['search_metadata']:
		next_results = data['search_metadata']['next_results']
		kwargs = dict([kv.split('=') for kv in (next_results[1:]).encode('utf-8').split("&")])
		data = twitter.search(**kwargs)
		statuses+=data['statuses']
		print("adding...")
	else:
		break


for post in statuses:
		tweet_record = post
		tweet_record['_id']=post['id_str']
		try:
			db['delhitweets'].insert(tweet_record)
		except:
			continue
			
	#print(post['id_str']+':'+post['text'])




