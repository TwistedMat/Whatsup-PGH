# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 20:19:01 2021

author: 
    Allison Michalowski amichalo@andrew.cmu.edu
Eshan Mehotra emehotr@andrew.cmu.edu
Sowjanya Manipal smanipal@andrew.cmu.edu

Imports to:
    WhatsUp_main_gui.py
"""

import tweepy
import pandas as pd
import time
import numpy as np
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import matplotlib.pyplot as plt


from matplotlib.figure import Figure

global api
def tweepysetup():
# Get the credentials for Tweepy1
    tweepycreds_df = pd.read_csv('tweepycreds.csv',header=None,names=['name','key'])
    
    # Extract Tweepy creds from csv
    consumer_key = tweepycreds_df.loc[tweepycreds_df['name'] == 'consumer_key ','key'].iloc[0]
    consumer_secret = tweepycreds_df.loc[tweepycreds_df['name'] == 'consumer_secret ','key'].iloc[0]
    access_token = tweepycreds_df.loc[tweepycreds_df['name'] == 'access_token ','key'].iloc[0]
    access_token_secret = tweepycreds_df.loc[tweepycreds_df['name'] == 'access_token_secret ','key'].iloc[0]
    
    # Connect to Tweepy using creds
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    global api
    api = tweepy.API(auth,wait_on_rate_limit=True)

#Setup Tweepy API
tweepysetup()

# Extraction Location data from tweets if available
def extract_location(line):
    if line['Location']:
        return line['Location'].full_name
    else:
        return None

# Function to extract tweets for multiple users at once
def scrape_multiusertweets():
    masterlist_tweets = []
    tweets_df = pd.DataFrame()
    try:
        userlist = ['PghEventsOffice','vstpgh','PNCParkEvents','heinzfield','CarnegieMellon','DowntownPitt']
        
        for user in userlist:
            maxcount=200
            # Creating query type using params
            tweets = tweepy.Cursor(api.user_timeline,id=user,tweet_mode='extended').items(maxcount)
            # Pulling information from tweets iterable object
            for tweet in tweets:
                masterlist_tweets.append((tweet.created_at, tweet.id_str, tweet.user.name, tweet.user.screen_name,tweet.user.description,
                        tweet.user.followers_count, tweet.user.statuses_count,tweet.full_text,
                        tweet.place, tweet.retweet_count, tweet.favorite_count, tweet.lang,
                        tweet.source))
                
            # Creation of dataframe from tweets list
            tweets_df = pd.DataFrame(masterlist_tweets,columns=['Tweet Datetime', 'Tweet Id','Twitter Name', 'Twitter at Name', 'Twitter User Bio',
                                                    'Twitter User Followers','Twitter User Total Tweets','Tweet Text', 'Location',
                                                    'Retweets', 'Favorites', 'Language', 'Source'])
            
            # Checks if there is location information available
            tweets_df['Location'] = tweets_df.apply(extract_location,axis=1)

            # Save DataFrame to csv
        tweets_df.to_csv('multiuser_tweets.csv', index = False)
        return tweets_df
    except BaseException as be:
        print('failed on_status',str(be))
        time.sleep(3)
        
        

# Username to scrape from
userlist = ['PghEventsOffice','vstpgh','PNCParkEvents','heinzfield','CarnegieMellon','DowntownPitt']

# Max recent tweets pulls N amount of most recent tweets from that user
max_tweets = 200

# Function will scrape username, attempt to pull max_tweet amount, and create csv file from data.


def gettweetDFs_live():
    # Read the csv again 
    usertweetdf = scrape_multiusertweets()
    
    
    # usertweetdf.head()
    User = usertweetdf.groupby('Twitter Name')
    # User.describe().head()
    # User.mean().sort_values(by="Favorites",ascending=False).head()
    
    # Get Relevant analysis params
    df1 = usertweetdf.groupby('Twitter Name')[['Twitter User Followers','Twitter User Total Tweets']].max().reset_index()
    df2 = usertweetdf.groupby('Twitter Name')[['Favorites','Retweets']].mean().reset_index()
    
    return usertweetdf,df1,df2

def gettweetDFs_arc(filename="multiuser_tweets.csv"):
    # Read the csv again 
    usertweetdf = pd.read_csv(filename, index_col=0)
    
    
    # usertweetdf.head()
    User = usertweetdf.groupby('Twitter Name')
    # User.describe().head()
    # User.mean().sort_values(by="Favorites",ascending=False).head()
    
    # Get Relevant analysis params
    df1 = usertweetdf.groupby('Twitter Name')[['Twitter User Followers','Twitter User Total Tweets']].max().reset_index()
    df2 = usertweetdf.groupby('Twitter Name')[['Favorites','Retweets']].mean().reset_index()
    
    return usertweetdf, df1, df2

#Shared axis bar graph
def plotAlltime(usertweetdf,df1,df2):
   # usertweetdf,df1,df2 = gettweetDFs(filename)
    xa = list(df1['Twitter Name'])
    # ya1 = list(df1['Twitter User Followers'])
    # ya2 = list(df1['Twitter User Total Tweets'])
    
    # Plot Bar1
    fig, axarr = plt.subplots(2,figsize=(10,5), dpi= 80, sharex = True)
    
    df1['Twitter User Followers'].plot(kind='bar', ax=axarr[0], color='tab:red',sharex=True) 
    
    # Plot Bar2
    df1['Twitter User Total Tweets'].plot(kind='bar', ax=axarr[1], color='tab:blue',sharex=True) 


    # Decorations
    axarr[1].set_xlabel('Twitter Name', fontsize=10)
    axarr[0].tick_params(axis='x', rotation=0, labelsize=10)
    axarr[0].set_ylabel('Favorites', color='tab:red', fontsize=10)
    axarr[0].tick_params(axis='y', rotation=0, labelcolor='tab:red' )
    axarr[0].grid(alpha=.4)
    
    axarr[1].set_ylabel("Reweets", color='tab:blue', fontsize=10)
    axarr[1].tick_params(axis='x', rotation=0, labelsize=10)
    axarr[1].tick_params(axis='y', labelcolor='tab:blue')
    axarr[0].set_title("All Time Twitter Popularity", fontsize=16)
    
    plt.xticks(np.arange(len(xa)),xa)
    fig.tight_layout()
    return fig
    # plt.savefig('Twitter_AllTimePopu.png')
    # plt.show()


def plotRecentAct(usertweetdf,df1,df2):
          
            
    #usertweetdf,df1,df2 = gettweetDFs()
    xb = df2['Twitter Name']
    yb1 = df2['Favorites']
    yb2 = df2['Retweets']
    
    # Plot Line1 (Left Y Axis)
    fig, ax1 = plt.subplots(1,1,figsize=(12,5), dpi= 80)
    ax1.plot(xb, yb1, color='tab:red')
    
    # Plot Line2 (Right Y Axis)
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(xb, yb2, color='tab:blue')
    
    # Decorations
    # ax1 (left Y axis)
    ax1.set_xlabel('Twitter Name', fontsize=10)
    ax1.tick_params(axis='x', rotation=0, labelsize=10)
    ax1.set_ylabel('Favorites', color='tab:red', fontsize=10)
    ax1.tick_params(axis='y', rotation=0, labelcolor='tab:red' )
    ax1.grid(alpha=.4)
    
    # ax2 (right Y axis)
    ax2.set_ylabel("Reweets", color='tab:blue', fontsize=10)
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_title("Popularity based on Recent Activity ( Past 200 Tweets )", fontsize=16)
    fig.tight_layout()
    return fig
    # plt.savefig('RecentPopu.png')
    # plt.show()

def plotWC(usertweetdf,df1,df2):
            
    #usertweetdf,df1,df2 = gettweetDFs(filename)
    
    # WordCloud Plotting Starts
    # Import Mask Image
    twitter_mask = np.array(Image.open("twittermask_bwnew.png"))
    
    # Join all Tweet text into one string
    text = " ".join(tweet for tweet in usertweetdf['Tweet Text'])
    #print ("There are {} words in the combination of all tweets.".format(len(text)))
    
    
    # Create stopword list:
    # StopWords Text File also created
    with open("newstopwordlist.txt") as file:
        allstopwords = [word.replace(',\n','') for word in file]
    
    # stopwords.update(allstopwords)
    stopwords = allstopwords + list(STOPWORDS)
    
    
    # Generate a word cloud image
    wordcloudall = WordCloud(width= 1024, height=728, stopwords=stopwords, background_color="black").generate(text)
    
    # Display the generated image:
    # the matplotlib way:
    # plt.imshow(wordcloudall, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()
    wordcloudall.to_file("first_review.png")
    
    # Masking on Twitter Logo
    twitter_mask = np.array(Image.open("twittermask_bwnew.png"))
    def transform_format(val):
        if val == 147:
            return 255
        else:
            return val
    # Transform your mask into a new one that will work with the function:
    transformed_twitter_mask = np.ndarray((twitter_mask.shape[0],twitter_mask.shape[1]), np.int32)
    
    for i in range(len(twitter_mask)):
        transformed_twitter_mask[i] = list(map(transform_format, twitter_mask[i]))
    
    # plt.imshow(transformed_twitter_mask)
    
    
    #Collocated False
    
    # Generate a word cloud image
    wordcloudall = WordCloud(width= 1024, height=728, stopwords=stopwords, background_color="black",mask=transformed_twitter_mask, contour_color='blue',contour_width=2).generate(text)
    
    # Display the generated image:
    # the matplotlib way:
    figw, axw = plt.subplots(1,figsize=(7,7), dpi= 80)
    plt.imshow(wordcloudall, interpolation='bilinear')
    plt.axis("off")
    return figw
    # wordcloudall.to_file("TwitterUserEvents_WordCloud.png")
    # plt.show()
    

if __name__ == "__main__":
    usertweetdf,df1,df2=gettweetDFs_live()
    usertweetdf,df1,df2= gettweetDFs_arc(filename="multiuser_tweets.csv")













