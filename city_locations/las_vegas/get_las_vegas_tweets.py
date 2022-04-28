import json
import twitter
import requests
from urllib.parse import unquote

#most of the code was taking from the Twitter Cookbook Ch.9 with some changes with respect to this project

def oauth_login():
    
   #Add your Consumer and Auth keys here to run code
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    OAUTH_TOKEN = ''
    OAUTH_TOKEN_SECRET = ''
   

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

### Uses tweepy to search and filter tweets to english language only

    auth1 = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    auth1.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    api = tweepy.API(auth1) 

    res = api.search('lang','en')
    for i in res:
        print( i.lang)

# ## Example 4. Searching for tweets


def twitter_search(twitter_api, q, max_results=200, **kw):

    # for details on advanced search criteria that may be useful for 
    # keyword arguments 
   
    search_results = twitter_api.search.tweets(q=q, count=200, geocode='42.3602534,-71.0582912,20mi', **kw)#new line added

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
# ## Example 11. Finding the most popular tweets in a collection of tweets


def find_popular_tweets(twitter_api, statuses, retweet_threshold=3):

    # You could also consider using the favorite_count parameter as part of 
    # this  heuristic, possibly using it to provide an additional boost to 
    # popular tweets in a ranked formulation
        
    return [ status
                for status in statuses 
                    if status['retweet_count'] > retweet_threshold ] 



q = 'Las Vegas'

twitter_api = oauth_login()
search_results = twitter_search(twitter_api, q, max_results=500)


popular_tweets = find_popular_tweets(twitter_api, search_results)

sorting = sorted(popular_tweets, key=lambda x: x['retweet_count'], reverse=True)

#printing the #1 popular tweet around a certain area
try:
  print("#1 popular tweet")
  print('retweet count:',sorting[0]['retweet_count'],';', sorting[0]['text'])
except:
    pass

#printing all popular tweets around a certain area
"""
print("\n") 
print("Popular tweets regarding retweet_count")
print("\n")
for i, t in enumerate(sorting):
  try:
    print(i, t['retweet_count'], t['text'])
  except:
    pass
"""

tweets1 = [r['user']['screen_name'] for r in sorting]
"""
from time import time
t = int(time())
with open('C:/Users/Users/imjus/Downloads/popular-tweets-%s-%s.txt' % (sorting[0]['id'], t), 'w') as f_out:
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
            
"""        
print('done')





#----------------------------------------------------------------
#Code to get the retweets from the a most popular tweet in a city


key = '8xjkwS2U7zCVnbDAQZOQJ7jP0'
secret = 'lMXmAcymoFXr3dm190bXY46pVUmaLogchtY48iwfxReP2a9VNo'


auth_url = 'https://api.twitter.com/oauth2/token'
data = {'grant_type': 'client_credentials'}
auth_resp = requests.post(auth_url, auth=(key, secret), data=data)
token = auth_resp.json()['access_token']


tweet_id = sorting[0]['id'] #passing the id of the user that has the most popular tweet
url = 'https://api.twitter.com/1.1/statuses/retweets/%s.json?count=100' % tweet_id
headers = {'Authorization': 'Bearer %s' % token}
retweets_resp = requests.get(url, headers=headers)
retweets = retweets_resp.json()
#print(retweets)
#print(json.dumps(retweets, indent=1))

#to get the screen name of each retweeter
retweeters = [r['user']['screen_name'] for r in retweets]



#Saving results into a file and adding unique time stamp
from time import time
t = int(time())
with open('C:/Users/imjus/Downloads/retweeters-%s-%s.txt' % (tweet_id, t), 'w') as f_out:
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






#-----------------------------------------------------------------------------
#Getting the location of the users that retweeted the most popular tweet
for tweet in retweets:
    print(tweet.get('user', {}).get('location', {}))


print()


#getting the lexical diversity
#from __future__ import division

def lexical_diversity(my_text_data):

  word_count = len(my_text_data)
  vocab_size = len(set(my_text_data))
  diversity_score = vocab_size / word_count
  return diversity_score


print('Lexical diveristy from the most popular tweet:',lexical_diversity(sorting[0]['text']))
print()


"""
#tokenization and getting rid  of the url at the end of the tweet
def tokenization(raw):
    import nltk, re, pprint
    from nltk import word_tokenize

    tokens = word_tokenize(raw)


    porter = nltk.PorterStemmer()
    lastoken = [porter.stem(t) for t in tokens]
    #print(lastoken)

    newlist = []
    for i in lastoken:
        
        if i == 'http':
            break
        else:
            newlist.append(i)

    return newlist


text1 = sorting[0]['text']
data = tokenization(text1)
print(data)
"""

print()

#----------------------------
#Finding whether the most popular tweet is positive, neutral, or negative
import tweepy
import re
from tweepy import OAuthHandler
from textblob import TextBlob

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



# picking positive tweets from tweets
tweet1 = get_tweet_sentiment(sorting[0]['text'])
print('the most popular tweet is:', tweet1)


for i,j in enumerate(sorting):
    sorting[i]['sentiment'] = (get_tweet_sentiment(j['text']))

for i in sorting:
    print(i['sentiment'], i['text'])

