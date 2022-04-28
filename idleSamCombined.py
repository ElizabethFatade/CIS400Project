import json
import twitter
import requests
from urllib.parse import unquote
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import numpy as np
import re
from textblob import TextBlob
from time import time

#most of the code was taking from the Twitter Cookbook Ch.9 with some changes with respect to this project

# Example 1
def oauth_login():
    
   # Add your Consumer and Auth keys here to run code
    CONSUMER_KEY = 'jcH8YTqUYYAj6zkZ2mMpgwXaA'
    CONSUMER_SECRET = 'Kd9jyen5tIJMydHZcXMPAxxXl4wJnnA7Rx7OQ9iFADxLIURbKY'
    OAUTH_TOKEN = '1156377747419279360-uQlwIThJtjyY57rzVGfdvavyWAokv0'
    OAUTH_TOKEN_SECRET = '5bhf3oHX6fLVmdBI3XxVa2E211exSxwjgiRyPRwsaLpCd'


    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api



# Example 4. Searching for tweets


def twitter_search(twitter_api, q,localArea,max_results=200, **kw):

    # for details on advanced search criteria that may be useful for 
    # keyword arguments 
    #localArea is string turned into suitable geocode entity
    
    search_results = twitter_api.search.tweets(q=q, count=200, geocode=localArea, **kw)#new line added

    statuses = search_results['statuses'] #statuses added
    
    
    # Enforce a reasonable limit
    max_results = min(1000, max_results)
    
    for _ in range(10): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError as e: # No more results when next_results doesn't exist
            break
            
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') for kv in unquote(next_results[1:]).split("&") ])
        
        search_results = twitter_api.search.tweets(**kwargs)
        
        statuses += search_results['statuses'] #statuses added
       
        if len(statuses) >= max_results: 
            break
            
    return statuses


#------------------------------------------------------------------------
# Example 11. Finding the most popular tweets in a collection of tweets

def find_popular_tweets(twitter_api, statuses, retweet_threshold=3):

    # You could also consider using the favorite_count parameter as part of 
    # this  heuristic, possibly using it to provide an additional boost to 
    # popular tweets in a ranked formulation
        
    return [ status
                for status in statuses 
                    if status['retweet_count'] > retweet_threshold ] 

#Finding local Area
def get_local_area(area):
    # Initialize Nominatim API,
    #which takes a string input and returns a latitude and longitude
    geolocator = Nominatim(user_agent="MyApp")

    location = geolocator.geocode(area)

    #print("The latitude of the location is: ", location.latitude)
    #print("The longitude of the location is: ", location.longitude)

    lat = str(location.latitude)
    long = str(location.longitude)
    
    #geocode takes data like this so we format it here and then returned
    local_Area = lat+','+long+',20mi' 
    return local_Area


#----------------------------------------------------------------
#Code to get the retweets from the a most popular tweet in a city

def get_retweets(pop_ID):
    # Add your Consumer keys here to run code
    key = 'jcH8YTqUYYAj6zkZ2mMpgwXaA'
    secret = 'Kd9jyen5tIJMydHZcXMPAxxXl4wJnnA7Rx7OQ9iFADxLIURbKY'

    auth_url = 'https://api.twitter.com/oauth2/token'
    data = {'grant_type': 'client_credentials'}
    auth_resp = requests.post(auth_url, auth=(key, secret), data=data)
    token = auth_resp.json()['access_token']


    tweet_id = pop_ID #passing the id of the user that has the most popular tweet
    url = 'https://api.twitter.com/1.1/statuses/retweets/%s.json?count=100' % tweet_id
    headers = {'Authorization': 'Bearer %s' % token}
    retweets_resp = requests.get(url, headers=headers)
    retweets = retweets_resp.json()
    return retweets


#getting the lexical diversity
def lexical_diversity(my_text_data):

  word_count = len(my_text_data)
  vocab_size = len(set(my_text_data))
  diversity_score = vocab_size / word_count
  return diversity_score


#----------------------------
#Finding whether the most popular tweets are positives, neutrals, or negatives
def clean_tweet(tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+) | ([ ^ 0-9A-Za-z \t]) (\w+: \/\/\S+)", " ", tweet).split())


def get_tweet_sentiment(tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'





q = 'Boston, MA'
localArea = get_local_area(q)

#Searching for tweets
twitter_api = oauth_login()
search_results = twitter_search(twitter_api, q, localArea, max_results=500)

#Fetching the popular tweets
popular_tweets = find_popular_tweets(twitter_api, search_results)

#Sorting all popular tweets
sorting = sorted(popular_tweets, key=lambda x: x['retweet_count'], reverse=True)


#printing the #1 popular tweet around a certain area
try:
  print("#1 popular tweet")
  print('retweet count:',sorting[0]['retweet_count'],';', sorting[0]['text'])
except:
    pass

#Most popular tweet's ID
tweet_id = sorting[0]['id']


#--------------------------------------------------------------------
#saving all popular tweets into a file by encoding the whole tweet so
#their urls can be saved as well as if there was an emoji

t = int(time())
with open('C:/Users/Users/imjus/Downloads/popular-tweets-%s-%s.txt' % (tweet_id, t), 'w') as f_out:
    f_out.write('#')
    f_out.write('\t')
    f_out.write('retweet #')
    f_out.write('\t')
    f_out.write('ID')
    f_out.write('\t')
    f_out.write('\t')
    f_out.write('\t')
    f_out.write('tweet')
    f_out.write('\n')
    for i, j in enumerate(sorting):
            f_out.write(str(i))
            f_out.write('\t')
            f_out.write(str(j['retweet_count']))
            f_out.write('\t')
            f_out.write(str(j['id']))
            f_out.write('\t')
            f_out.write(str(j['text'].encode("utf-8")))
            f_out.write('\n')
            
      
print('done')


#getting all the retweets from the most popular tweet
retweets = get_retweets(tweet_id)

#to get the screen name of each retweeter
retweeters = [r['user']['screen_name'] for r in retweets]


#Saving the retweeters and their locations into a file and adding unique time stamp
from time import time
t = int(time())
with open('C:/Users/leigh/Downloads/json_stuff/retweeters-%s-%s.txt' % (tweet_id, t), 'w') as f_out:
    for r, tweet in zip(retweeters, retweets):
        f_out.write(r)
        f_out.write('\t')
        f_out.write('\t')
        try:
            f_out.write(tweet.get('user', {}).get('location', {}))
        except:
            pass
        
        f_out.write('\n')
print('done')




print('Lexical diveristy from the most popular tweet:',
      lexical_diversity(sorting[0]['text']))
print()

#-----------------------------------------------------------------------------
#Getting the location of the users that retweeted the most popular tweet
#to calculate the percent of local and nonlocal retweets
localRT = 0
totalRT = int(sorting[0]['retweet_count']) 

print("---Retweeters' locations from the most popular tweet---")
for tweet in retweets:
    print(tweet.get('user', {}).get('location', {}))
    if (str(tweet.get('user', {}).get('location', {}))) == q:
        localRT = localRT + 1
    if (str(tweet.get('user', {}).get('location', {}))) == '':
        totalRT = totalRT - 1

nolocalRT = totalRT - localRT

print()
print("Total retweets: ",totalRT)
print("Number of local retweets: ",localRT)
print("Number of non-local retweets: ",nolocalRT)
print()




#Getting sentiment Analysis from the popular tweets

ptweet=0
ntweet=0
negtweet=0
totalTweet = len(sorting)

for i,j in enumerate(sorting):
    sorting[i]['sentiment'] = (get_tweet_sentiment(j['text']))

# picking positive tweets from tweets
ptweets = [tweet for tweet in sorting if tweet['sentiment'] == 'positive']
ptweet = len(ptweets)
# percentage of positive tweets
print("Positive tweets percentage: {} %".format(
        100*len(ptweets)/len(sorting)))

# picking negative tweets from tweets
ntweets = [tweet for tweet in sorting if tweet['sentiment'] == 'negative']
negtweet = len(ntweets)
# percentage of negative tweets
print("Negative tweets percentage: {} %".format(
        100*len(ntweets)/len(sorting)))

# percentage of neutral tweets
print("Neutral tweets percentage: {} % \
        ".format(100*(len(sorting) - (len(ntweets)+len(ptweets)))/len(sorting)))

ntweet = totalTweet - (ptweet+negtweet)

print('The most popular tweet is:', sorting[0]['sentiment'])

#----------------------------------------------------------------------------
#printing out the tweets data in pie charts using matplotlib
percentLocal = round(((localRT/(totalRT))*100),2)
percentNonLocal = round(100 - percentLocal,2)


#create an array of your data, we only have 2, and an array in order of your labels
#myexplode just spearates the data a little bit
y = np.array([percentLocal, percentNonLocal])
mylabels = ["Local Retweets", "Non-local Retweets"]
myexplode = [0.1, 0]

#plot all the data and include the lables as well as data numbers on each area of data to clearly show results
plt.title(q)
plt.pie(y, labels = mylabels,autopct=lambda p: '{:.2f}%'.format(p), explode = myexplode, shadow = True)
plt.show()
"""-----------------------------------------------------------------------"""
#enter number of positive tweets and total tweets, divide positive sentiment over total and multiply by 100 for percent. Then do 100-positive for negative percent. 


percentPosSentiment = round(((ptweet/(totalTweet))*100),2)
percentNegSentiment = round(((ntweet/totalTweet)*100),2)
percentNeuSentiment = round(((negtweet/totalTweet)*100),2)


#create an array of your data, we only have 2, and an array in order of your labels
#myexplode just spearates the data a little bit
y = np.array([percentPosSentiment, percentNegSentiment, percentNeuSentiment])
mylabels = ["Positive Sentiment", "Negative Sentiment", "Neutral Sentiment"]
myexplode = [0.1, 0, 0]

#plot all the data and include the lables as well as data numbers on each area of data to clearly show results
plt.pie(y, labels = mylabels,autopct=lambda p: '{:.2f}%'.format(p), explode = myexplode, shadow = True)
plt.title("Sentiment Analysis")
plt.show()
