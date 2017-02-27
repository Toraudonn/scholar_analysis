import json
import csv
import os
import sys

import requests
import praw

import time

from secret import Reddit

red_o = Reddit()

reddit = praw.Reddit(client_id=red_o.client_id,
                     client_secret=red_o.client_secret,
                     user_agent=red_o.user_agent)



date = time.strftime("%d/%m/%Y")
f = open('mlreddit.csv', 'a')
for submission in reddit.subreddit('MachineLearning').top('day', limit=10):
    title = submission.title
    url = submission.url
    shortlink= submission.shortlink
    
    print("+---------------------------+")
    print(title)
    print(url)
    print(shortlink)
    
    data = [date, title, url, shortlink]
    writer = csv.writer(f)
    writer.writerow(data)
    
for submission in reddit.subreddit('datascience').top('day', limit=10):
    title = submission.title
    url = submission.url
    shortlink= submission.shortlink
    
    print("+---------------------------+")
    print(title)
    print(url)
    print(shortlink)
    
    data = [date, title, url, shortlink]
    writer = csv.writer(f)
    writer.writerow(data)
f.close()

