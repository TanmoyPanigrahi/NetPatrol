#!/usr/bin/python2.7

import praw
import pdb
import re
import os
import numpy
import datetime
import whois
import json
import urllib
import ssl

# Searching for...
# Posting cycles
# Are they actively involved in campaigns: a lil more specified
# Do they respond to third person: a lil more specified
# Users that go silent for long periods of time
# Copied and pasting content
# Follower-following ratio
# Age of account
# Name of account

# NEW FILTERS
# Interactivity
# Mainstream news articles
# Unreputable news sources

# LIMIT VALUES
author_limit = 1
comment_limit = 20

# THRESHOLD VALUES
std_threshold = 10
age_threshold = 1500000
comment_threshold = 10
search_threshold = 10000
date_threshold = datetime.datetime(2000, 1, 1, 1, 1, 1)
vote_threshold = 10
upvote_ratio_threshold = .1
punc_threshold = .1

the_posts = []
filter_one = [] # this is repeat posts
filter_two = [] # posting cycles

total_score = 100

reddit = praw.Reddit(client_id='SqsNOmnAF3Oy9Q',
                     client_secret='fZMtD8aWsG6OJ1Kck3sQxVW2BvA',
                     user_agent='MyFilterBot_44712')
now = int(datetime.datetime.timestamp(datetime.datetime.today()))

domain_trust = [".com", ".org", ".gov", ".edu", ".net"]

authors_analyzed = []

print("ANALYZING...")

# USING CUSTOM SEARCH ENGINE
def results(searchfor):
    f = open("key.txt", "r")
    key = f.read()
    g = open("cx.txt", "r")
    cx = g.read()
    query = urllib.parse.urlencode({'q': searchfor})
    url = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s' % (key, cx, query)
    context = ssl._create_unverified_context()
    search_response = urllib.request.urlopen(url, context=context)
    search_results = search_response.read()
    results = json.loads(search_results)
    data = results["queries"]["request"][0]["totalResults"]
    return int(data)

counter = 0;

subreddit = reddit.subreddit('pythonforengineers')

for submission in subreddit.hot(limit=author_limit):
    # BEGIN LINK ANALYSIS
    if "http" in submission.selftext or "http" in submission.title:
        url = ""
        text = ""
        if "http" in submission.selftext:
            text = submission.selftext
        else:
            text = submission.title
        i = text.find("http")
        if i > 0:
            while i < len(text) and text[i] != " ":
                url += text[i]
                i = i + 1
        good_domain = False
        for end in domain_trust:
            good_domain = True
            if end in url:
                index = text.rfind(end)
                if text[index + 1] == ".":
                    # risk factor calculation
                    good_domain = False
                else:
                    domain = ""
                    i = text.find(end) - 1
                    while i > 0 and (text[i] is not "/" and text[i] is not "."):
                        domain = text[i] + domain
                        i = i - 1
                    domain += end
                    print(domain)
                    # WE HAVE COLLECTED THE DOMAIN
                    searchString = "link:" + domain
                    results = results(searchString)
                    print(results)
                    if results < search_threshold:
                        # risk factor calculation
                        print("Not too many results")
                    w = whois.whois(domain)
                    w_date = w.creation_date
                    print("Date of creation ", w_date)
                    if w_date > date_threshold:
                        # risk factor calculation
                        print("New site")
if not good_domain:
    # risk factor calculation
    print("Domain is not valid")
        
    if "https" not in text:
        # risk factor calculation
        print("not secure")
# END LINK ANALYSIS

# BEGIN COMMENT ANLAYSIS
if submission.num_comments > comment_threshold:
    # risk factor calculation
    print("There are a lot of comments")
    # END COMMENT ANALYSIS
    
    # BEGIN VOTE ANALYSIS
    total_votes = submission.score / submission.upvote_ratio
    if total_votes > vote_threshold:
        # risk factor calculation
        print("There are a lot of votes")
        if submission.upvote_ratio < upvote_ratio_threshold:
            # risk factor calculation
            print("There are many downvotes")
# END VOTE ANALYSIS


# BEGIN PUNCTUATION ANALYSIS
inc = 0
for s in text:
    if s == "!" or s == s.upper():
        inc = inc + 1
ratio = inc / len(text)
if ratio > punc_threshold:
    # risk factor calculation
    print("There's a lot of weird punctuation")
    # END PUNCTUATION ANALYSIS
    
    if submission.author not in authors_analyzed:
        counter = counter + 1;
        authors_analyzed.append(submission.author)



print("Beginning in depth analysis")
# BEGIN AUTHOR ANALYSIS
filter_two_count = 0
filter_one_count = 0
previous_created = 0
for author in authors_analyzed:
    # POSTING CYCLES
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
    if std > std_threshold:
        if author not in filter_one:
            filter_one.append(author)
            filter_one_count = filter_one_count + 1
            print("Filter one: ", author)
    # AGE OF ACCOUNT
    age = author.created_utc
    time = int(now) - int(age)
    if time < age_threshold:
        if author not in filter_two:
            filter_two_count = filter_two_count + 1
            filter_two.append(author)
            print("Filter two ", author)
if counter == 0:
    accuracy_one = 0
    accuracy_two = 0
else:
    accuracy_one = (float(filter_one_count)/float(counter))
    accuracy_two = (float(filter_two_count)/float(counter))
