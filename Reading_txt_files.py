"""
If you decide to split the work of fetching tweets and then do its sentiment analysis, you can
use this file to read the tweets saved in a text file. Therefore, it is up to the user. In our case,
since we were able to integrate both fetching and doing the sentiment analysis, for our final application
we did not implement it.
"""
#function to clean tweets from unicode data
def unicode_to_plain(text):

    TEXT = (text.
    		replace('\\xe2\\x80\\x99', "").
            replace('\\xc3\\xa9', '').
            replace('\\xe2\\x80\\x90', '').
            replace('\\xe2\\x80\\x91', '').
            replace('\\xe2\\x80\\x92', '').
            replace('\\xe2\\x80\\x93', '').
            replace('\\xe2\\x80\\x94', '').
            replace('\\xe2\\x80\\x94', '').
            replace('\\xe2\\x80\\x98', "").
            replace('\\xe2\\x80\\x9b', "").
            replace('\\xe2\\x80\\x9c', '').
            replace('\\xe2\\x80\\x9c', '').
            replace('\\xe2\\x80\\x9d', '').
            replace('\\xe2\\x80\\x9e', '').
            replace('\\xe2\\x80\\x9f', '').
            replace('\\xe2\\x80\\xa6', '').
            replace('\\xe2\\x80\\xb2', "").
            replace('\\xe2\\x80\\xb3', "").
            replace('\\xe2\\x80\\xb4', "").
            replace('\\xe2\\x80\\xb5', "").
            replace('\\xe2\\x80\\xb6', "").
            replace('\\xe2\\x80\\xb7', "").
            replace('\\xe2\\x81\\xba', "").
            replace('\\xe2\\x81\\xbb', "").
            replace('\\xe2\\x81\\xbc', "").
            replace('\\xe2\\x81\\xbd', "").
            replace('\\xe2\\x81\\xbe', "").
            replace('\\xe2\\x81\\xa9', "").
            replace('\\xe2\\x81\\xa6', "").
            replace('\\xe2\\x80\\xa2', "").
            replace('\\xe2\\x80\\xbc', "")

                 )
    return TEXT

#reading the txt file as bytes
with open("path_and _name_file", "rb") as f:
    tweets = f.readlines()
            
     
print('done')

#decoding the list of tweets
for i, j in enumerate(tweets):
    tweets[i] = j.decode("utf-8")

#cleaning tweets
for i, j in enumerate(tweets):
    tweets[i] = j.replace("b'", "")
    
#cleaning tweets by getting rid of unicode data
for i, j in enumerate(tweets):
    tweets[i] = unicode_to_plain(j)

#printing tweets to verify 
for i in tweets:
    print(i)

