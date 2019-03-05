#!/usr/bin/python2.7

import praw
import pdb
import re
import os
import numpy
import datetime

#Searching for...
#Posting cycles
#Are they actively involved in campaigns: a lil more specified
#Do they respond to third person: a lil more specified
#Users that go silent for long periods of time
#Copied and pasting content
#Follower-following ratio
#Age of account
#Name of account - Does it resemble a famous person?

author_limit = 20
comment_limit = 20
char_limit = 0
age_limit = 1500000
std_limit = 0

reddit = praw.Reddit('bot1')
now = int(datetime.datetime.timestamp(datetime.datetime.today()))

the_posts = []
filter_one = [] # this is repeat posts
filter_two = [] # this is age of account
filter_three = [] # posting cycles

authors_analyzed = []

print("ANALYZING...")
#step 1: collecting all the authors
counter = 0;
subreddit = reddit.subreddit('pythonforengineers')
for submission in subreddit.hot(limit=author_limit):
    if submission.author not in authors_analyzed:
        counter = counter + 1;
        print(submission.author)
        authors_analyzed.append(submission.author)


print()
filter_one_count = 0;
print("FILTER ONE BOTS?...")
#TEST 1: search for duplicates
for author in authors_analyzed:
    for post in author.comments.new(limit=comment_limit):
        if reddit.comment(id=post).body not in the_posts:
            the_posts.append(reddit.comment(id=post).body)
        else:
            if len(reddit.comment(id=post).body) > char_limit and author not in filter_one:
                filter_one_count = filter_one_count + 1;
                filter_one.append(author)
                print(author)
if counter == 0:
    accuracy_one = 0
else:
    accuracy_one = (float(filter_one_count)/float(counter))
print("Accuracy: " + str(accuracy_one))
print()

#TEST 2: Age of account
filter_two_count = 0
print("FILTER TWO BOTS?...")
for author in authors_analyzed:
    age = author.created_utc
    time = int(now) - int(age)
    if time < age_limit:
        if author not in filter_two:
            filter_one_count = filter_two_count + 1
            filter_two.append(author)
            print(author)
if counter == 0:
    accuracy_two = 0
else:
    accuracy_two = (float(filter_two_count)/float(counter))
print("Accuracy: " + str(accuracy_two))
print()

#TEST 3: Posting Cycles
print("FILTER THREE BOTS?...")
filter_three_count = 0
previous_created = 0
for author in authors_analyzed:
    author_timechange = []
    for post in author.comments.new(limit=comment_limit):
        created = int(post.created)
        if previous_created != 0:
            deltat = created - previous_created # to get gap between posting
            author_timechange.append(deltat)
            previous_created = created
        else:
            previous_created = created
    std = numpy.std(author_timechange)
    if std > std_limit:
        if author not in filter_three:
            filter_three.append(author)
            filter_three_count = filter_three_count + 1
            print(author)
if counter == 0:
    accuracy_three = 0
else:
    accuracy_three = (float(filter_three_count)/float(counter))
print("Accuracy: " + str(accuracy_three))
print()

#CONGLOMERATE THEM
congl = 0
print("PREDICTION")
prediction_bots = []
for author in authors_analyzed:
    score = 0
    if author in filter_one:
        score = score + 7
    if author in filter_two:
        score = score + 4
    if author in filter_three:
        score = score + 5
    if score > 10:
        prediction_bots.append(author)
        congl = congl + 1
        print("HIGH RISK: " + str(author))
if counter == 0:
    accuracy_congl = 0
else:
    accuracy_congl = (float(congl)/float(counter))
print("Accuracy: " + str(accuracy_congl))
print()
