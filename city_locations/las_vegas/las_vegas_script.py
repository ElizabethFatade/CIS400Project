import tweepy
import re
from tweepy import OAuthHandler
from textblob import TextBlob
import matplotlib.pyplot as plt
import numpy as np
import nltk
from nltk import word_tokenize
#libraries to create a wordcloud from positive, negative, and neutral popular tweets
from wordcloud import WordCloud, STOPWORDS

# Class gives a percentage for what percentage of tweets are positive
# negative and or neutral in Las Vegas


class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'LSwCnmkUeRE3xZCIK0fhLwt7x'
        consumer_secret = 'ytlg2rg01wBQ1SZ60pga5L7psE6tSAPOHQm6H6aGREML76NV28'
        access_token = '1184965224396480512-Fz5YFsOZXSaH5vGqQVPw7cEBkaKv8V'
        access_token_secret = 'O8iqQ2M7ja3F3No1HNnTlHyNfTN1Ze0NgNB2B34afl713'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+) | ([ ^ 0-9A-Za-z \t]) (\w+: \/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search_tweets(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(
                    tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepyException as e:
            # print error (if any)
            print("Error : " + str(e))


#tokenazing tweet's text and turning every character to lowercase
def tokenization(raw):

    tokens = word_tokenize(raw)
    lastoken = [t.lower() for t in tokens]
    return lastoken


def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = api.get_tweets(query='Las Vegas, NV', count=200)
    totalTweet = len(tweets)

    #cleaning once again all popular tweets to get rid of url links
    pattern = re.compile(r'(https?://)?(www\.)?(\w+\.)?(\w+)(\.\w+)(/.+)?')
    for i, j in enumerate(tweets):
        tweets[i]['text'] = re.sub(pattern,'',j['text'])

    
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(
        100*len(ptweets)/len(tweets)))
    ptweet = len(ptweets)
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(
        100*len(ntweets)/len(tweets)))
    negtweet = len(ntweets)
    # picking neutral tweets from tweets
    netweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    neutweet = len(netweets)
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} % \
        ".format(100*(len(tweets) - (len(ntweets)+len(ptweets)))/len(tweets)))

    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:10]:
        print(tweet['text'])

    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:10]:
        print(tweet['text'])


    #-------------------------------------------------------------------------------------
    #enter number of positive tweets and total tweets, divide positive sentiment
    #over total and multiply by 100 for percent. Then do 100-positive for negative percent. 


    percentPosSentiment = round(((ptweet/(totalTweet))*100),2)
    percentNegSentiment = round(((negtweet/totalTweet)*100),2)
    percentNeuSentiment = round(((neutweet/totalTweet)*100),2)


    #create an array of your data, we only have 2, and an array in order of your labels
    #myexplode just spearates the data a little bit
    y = np.array([percentPosSentiment, percentNegSentiment, percentNeuSentiment])
    mylabels = ["Positive Tweets", "Negative Tweets", "Neutral Tweets"]
    myexplode = [0.1, 0, 0]

    #plot all the data and include the lables as well as data numbers on each area of data to clearly show results
    plt.pie(y, labels = mylabels,autopct=lambda p: '{:.2f}%'.format(p), explode = myexplode, shadow = True)
    plt.title("Sentiment Analysis in Popular Tweets")
    plt.show()




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



    

if __name__ == "__main__":
    # calling main function
    main()
