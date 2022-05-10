#This program file get a collection of most popular tweets, their sentiment analysis, and the retweets from the most
#popular tweet to analize the the constrains betweet Local and Non-Local retweets.
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
import nltk
from nltk import word_tokenize
#libraries to create a wordcloud from positive, negative, and neutral popular tweets
from wordcloud import WordCloud, STOPWORDS

#most of the code was taking from the Twitter Cookbook Ch.9 with some changes with respect to this project

# Example 1
def oauth_login():
    
   #*******Add your Consumer and Auth keys here to run code********
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    OAUTH_TOKEN = ''
    OAUTH_TOKEN_SECRET = ''


    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api



#----------------------------
#Finding whether the most popular tweets are positives, neutrals, or negatives
def clean_tweet(tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) (\w+:\/\/\S+)", " ", tweet).split())


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
    #*******Add your Consumer keys here to run code******
    key = ''
    secret = ''

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



#function to remove emojies from tweets
def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


#tokenazing tweet's text and turning every character to lowercase
def tokenization(raw):

    tokens = word_tokenize(raw)
    lastoken = [t.lower() for t in tokens]
    return lastoken


#Area key
q = 'San Francisco, CA'
localArea = get_local_area(q)

#Searching for tweets
twitter_api = oauth_login()
search_results = twitter_search(twitter_api, q, localArea, max_results=500)

#Fetching the popular tweets
popular_tweets = find_popular_tweets(twitter_api, search_results)

#Sorting all popular tweets
sorting = sorted(popular_tweets, key=lambda x: x['retweet_count'], reverse=True)

#cleaning all popular tweets
for i, j in enumerate(sorting):
    sorting[i]['text'] = TextBlob(clean_tweet(j['text']))

#getting rid of emojis on all popular tweets
for i, j in enumerate(sorting):
    sorting[i]['text'] = remove_emoji(str(j['text']))
    
#printing the #1 popular tweet around a certain area
try:
  print("#1 popular tweet")
  print('retweet count:',sorting[0]['retweet_count'],';', sorting[0]['text'])
except:
    pass

#cleaning once again all popular tweets to get rid of url links
pattern = re.compile(r'(https?://)?(www\.)?(\w+\.)?(\w+)(\.\w+)(/.+)?')
for i, j in enumerate(sorting):
    sorting[i]['text'] = re.sub(pattern,'',j['text'])



#Most popular tweet's ID
tweet_id = sorting[0]['id']


#--------------------------------------------------------------------
#saving all popular tweets into a file by encoding the whole tweet so
#their urls can be saved as well as if there was an emoji
#it is up to the user to uncomment the following lines of code to save
#all popular tweets into a txt file. This only applies if the work is splitted
"""
t = int(time())
with open('path_folder/popular-tweets-%s-%s.txt' % (tweet_id, t), 'w') as f_out:
    for i, j in enumerate(sorting):
            f_out.write(str(j['text'].encode("utf-8")))
            f_out.write('\n')
            
"""  
print('done')


#getting all the retweets from the most popular tweet
retweets = get_retweets(tweet_id)

#to get the screen name of each retweeter
retweeters = [r['user']['screen_name'] for r in retweets]


#Saving the retweeters and their locations into a file and adding unique time stamp
#it is up to the user to uncomment the following lines of code to save
#the user ids and their loations of retweeters into a txt file. 
"""
t = int(time())
with open('path_folder/retweeters-users-%s-%s.txt' % (tweet_id, t), 'w') as f_out:
    for r, tweet in zip(retweeters, retweets):
        f_out.write(r)
        f_out.write('\t')
        f_out.write('\t')
        try:
            f_out.write(tweet.get('user', {}).get('location', {}))
        except:
            pass
        
        f_out.write('\n')
"""
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
#-------------------------------------------------------------------------
# picking positive tweets from tweets
ptweets = [tweet for tweet in sorting if tweet['sentiment'] == 'positive']
ptweet = len(ptweets)
# percentage of positive tweets
print("Positive tweets percentage: {} %".format(
        100*len(ptweets)/len(sorting)))


#-------------------------------------------------------------------------
# picking negative tweets from tweets
ntweets = [tweet for tweet in sorting if tweet['sentiment'] == 'negative']
negtweet = len(ntweets)
# percentage of negative tweets
print("Negative tweets percentage: {} %".format(
        100*len(ntweets)/len(sorting)))


#-------------------------------------------------------------------------
# picking neutral tweets from tweets
netweets = [tweet for tweet in sorting if tweet['sentiment'] == 'neutral']
neutweet = len(netweets)
# percentage of neutral tweets
print("Neutral tweets percentage: {} % \
        ".format(100*(len(sorting) - (len(ntweets)+len(ptweets)))/len(sorting)))

ntweet = totalTweet - (ptweet+negtweet)


#-------------------------------------------------------------------------
print('The most popular tweet is:', sorting[0]['sentiment'])



#-------------------------------------------------------------------------------------
#enter number of positive tweets and total tweets, divide positive sentiment
#over total and multiply by 100 for percent. Then do 100-positive for negative percent. 


percentPosSentiment = round(((ptweet/(totalTweet))*100),2)
percentNegSentiment = round(((negtweet/totalTweet)*100),2)
percentNeuSentiment = round(((ntweet/totalTweet)*100),2)


#create an array of your data, we only have 2, and an array in order of your labels
#myexplode just spearates the data a little bit
y = np.array([percentPosSentiment, percentNegSentiment, percentNeuSentiment])
mylabels = ["Positive Tweets", "Negative Tweets", "Neutral Tweets"]
myexplode = [0.1, 0, 0]

#plot all the data and include the lables as well as data numbers on each area of data to clearly show results
plt.pie(y, labels = mylabels,autopct=lambda p: '{:.2f}%'.format(p), explode = myexplode, shadow = True)
plt.title("Sentiment Analysis in Popular Tweets")
plt.show()





#------------------------------------------------------------
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


"""
In order to find what makes every positive, negative, and neutral in all popular
tweets, our team created a function to tokenize and change to lower case all
twets from every section.
"""

#all positive popular tweets
s = []
for i, j in enumerate(ptweets):
    ptweets[i]['text'] = tokenization(j['text'])
    s.append(','.join(ptweets[i]['text']))

sp = ','.join(s)

#all negative popular tweets
t = []
for i, j in enumerate(ntweets):
    ntweets[i]['text'] = tokenization(j['text'])
    t.append(','.join(ntweets[i]['text']))

sn = ','.join(t)


#all neutral popular tweets
u = []
for i, j in enumerate(netweets):
    netweets[i]['text'] = tokenization(j['text'])
    u.append(','.join(netweets[i]['text']))

sne = ','.join(u)


# Deleting any word which is less than 3-characters mostly those are stopwords
sp = re.sub(r'\b\w{1,2}\b', '', sp)
sn = re.sub(r'\b\w{1,2}\b', '', sn)
sne = re.sub(r'\b\w{1,2}\b', '', sne)

#-----------------------------------------------------------------------------

stopwords = set(STOPWORDS)

try:
    #Word Cloud for positive popular tweets
    wordcloudimage = WordCloud(
                              max_words=100,
                              max_font_size=500,
                              font_step=2,
                              stopwords=stopwords,
                              background_color='green',
                              width=1000,
                              height=720
                              ).generate(sp)


    plt.figure(figsize=(10,5))
    plt.axis("off")
    plt.imshow(wordcloudimage)
    wordcloudimage
    plt.show()
except:
    pass

try:
    #Word Cloud for negative popular tweets
    wordcloudimage = WordCloud(
                              max_words=100,
                              max_font_size=500,
                              font_step=2,
                              stopwords=stopwords,
                              background_color='black',
                              width=1000,
                              height=720
                              ).generate(sn)


    plt.figure(figsize=(10,5))
    plt.axis("off")
    plt.imshow(wordcloudimage)
    wordcloudimage
    plt.show()
except:
    pass

try:
    #Word Cloud for neutral popular tweets
    wordcloudimage = WordCloud(
                              max_words=100,
                              max_font_size=500,
                              font_step=2,
                              stopwords=stopwords,
                              background_color='white',
                              width=1000,
                              height=720
                              ).generate(sne)


    plt.figure(figsize=(10,5))
    plt.axis("off")
    plt.imshow(wordcloudimage)
    wordcloudimage
    plt.show()

except:
    pass



