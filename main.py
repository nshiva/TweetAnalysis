from flask import Flask, render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
import collections
from collections import defaultdict


app = Flask(__name__)

#app.config['MONGO2_DBNAME'] = 'jnan'
#mongo = PyMongo(app, config_prefix='MONGO2')

connection = MongoClient()
db=connection['jnan']

 
@app.route("/")
def index():
    return "This is the home page! "
 



@app.route('/analysis')
def analysis():
	#c = db['tweets'].count()
	tweets=db['tweets'].find()
	delhiTweets = db['delhitweets'].find()

	#Mumbai Rains
	tweetRetweets = GetRetweetCount(tweets) #T & RT
	tags = GetTopTenHashTags(db['tweets'].find())
	mumbaiLocations = GetLocationCounts(db['tweets'].find(),'Mumbai')
	mumbaiTweetTypes = GetTweetTypes(db['tweets'].find())
	mumbaiFavorites =  GetfavouritesofOriginalTweets(db['tweets'].find())
	wordCloudText = GetWordsForWordCloud(db['tweets'].find())
	mumbaiWeeks = analyseByWeek(db['tweets'].find())

	#Delhi Air Pollution
	delhiTweetRetweets = GetRetweetCount( db['delhitweets'].find())
	delhiTags = GetTopTenHashTags(db['delhitweets'].find())
	delhiLocations = GetLocationCounts(db['delhitweets'].find(),'Delhi')
	delhiTweetTypes = GetTweetTypes(db['delhitweets'].find())
	delhiFavorites =  GetfavouritesofOriginalTweets(db['delhitweets'].find())
	delhiWeeks = analyseByWeek(db['delhitweets'].find())


	return  render_template("analysis.html",tags=tags,tweetRetweets=tweetRetweets,mumbaiLocations=mumbaiLocations,mumbaiTweetTypes=mumbaiTweetTypes,mumbaiFavorites=mumbaiFavorites,wordCloudText=wordCloudText,mumbaiWeeks=mumbaiWeeks,
			delhiTags=delhiTags,delhiTweetRetweets=delhiTweetRetweets,delhiTweetTypes=delhiTweetTypes,delhiLocations=delhiLocations,delhiFavorites=delhiFavorites,delhiWeeks=delhiWeeks)





def analyseByWeek(tweets):
	weeks={}
	for tweet in tweets:
		week=tweet['created_at'][:3].encode('utf-8')
		if(week in weeks):
			weeks[week]+=1
		else:
			weeks[week]=1
	result=[["Week","No of Tweets"]]	
	for k,v in weeks.items():
		result.append([k,v])
	return(result)


def GetWordsForWordCloud(tweets):
	text = ""
	for tweet in tweets:
		text=text+" "+tweet['text']
		break
	return text






def GetfavouritesofOriginalTweets(tweets):
	a=0
	newArray=[]
	retweets={}
	for tweet in tweets:
		if 'retweeted_status' not in tweet: 				
			retweets[tweet['_id'].encode('utf-8')]=tweet['favorite_count']	

	dd = defaultdict(list)
	for k, v in retweets.iteritems():
		dd[v].append(k)

	 #dd{count:tweet ids}
	for k,v in dd.iteritems():
		dd[k]=len(v)
	#return(dict(dd))
	newArray.append(["No of Favorites","No of Tweets"])
	for k,v in dict(dd).iteritems():
		newArray.append([k,v])
	return newArray

def GetRetweetCount(tweets):
	retweets=0
	original=0
	for tweet in tweets:
		if 'retweeted_status' in tweet: 
			retweets+=1
		else:
			original+=1	
	return [["Type of Tweet","Freaquency"],["Original Tweets",original],["Retweets",retweets]]



def GetTweetTypes(tweets):
	textCount=0
	photoCount=0
	textPhotoCount=0
	for tweet in tweets:
		if('media' in tweet['entities']):
			for media in tweet['entities']['media']:
				if media['type']=='photo' and len(tweet['text']):
					textPhotoCount+=1
					break
				elif(media['type']=='photo'):
					photoCount+=1
					break
				
		elif(len(tweet['text'])):
			textCount+=1
	return(["Tweet Type","Count"],["Text Only",textCount],["Image Only",photoCount],["Text+ Image",textPhotoCount])
		
def GetTopTenHashTags(tweets):
	freaquencies = {}
	for tweet in tweets:
		hashtags=tweet['entities']['hashtags']
		for tag in hashtags:
			if(tag['text'].encode('utf-8').upper() in freaquencies.keys()):
				freaquencies[tag['text'].encode('utf-8').upper()]+=1
			else:
				freaquencies[tag['text'].encode('utf-8').upper()]=1
	stats = collections.Counter(freaquencies)
	top=stats.most_common(15)
	newArray=[]
	for t in top:
		newArray.append({'text':list(t)[0],'size':list(t)[1]/5})
	return newArray



def GetLocationCounts(tweets,loc):
	emptyLocations=0
	mumbaiCount=0
	nonMumbai=0
	for tweet in tweets:
		location=tweet['user']['location'].encode('utf-8')
		if(len(location)):
			if(loc.upper() in location.upper()):
				mumbaiCount+=1
			else:
				nonMumbai+=1
				print(location)
		else:
			emptyLocations+=1
	return [["Location","No of Tweets"],["No data available",emptyLocations],[loc,mumbaiCount],["Non "+loc,nonMumbai]]	



if __name__ == "__main__":
    app.run()


