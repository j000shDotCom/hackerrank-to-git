"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)

 Relevant Links:
 https://www.hackerrank.com/rest/contests/master/submissions/grouped?offset=0limit=2
 https://www.hackerrank.com/rest/hackers/{username}/recent_challenges?offset=0&limit=2
 https://www.hackerrank.com/rest/contests/master/challenges/{slug or challengeId}
 https://www.hackerrank.com/rest/contests/master/submissions/{submissionId}
 https://www.hackerrank.com/rest/contests/master/challenges/{slug}/submissions/?offset=0&limit=10
"""

import re
import json
import argparse
import pickle
import os.path
import itertools
import functools
from sh import git
from os import makedirs, chdir
from requests import Request, Session

def getArgParser():
    parser = argparse.ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-l', '--local', action='store', type=bool, metavar='local', help='local git repo')
    parser.add_argument('-r', '--remote', action='store', type=str, metavar='remote', help='remote git repo URL')
    parser.add_argument('-f', '--file', action='store', type=bool, metavar='file', help='parse HAR file')
    parser.add_argument('-d', '--daemon', action='store_true', default=False, help='run in background')
    parser.add_argument('-u', '--username', action='store', metavar='username', help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', help='account password')
    return parser;

def login(s, username, password):
    csrf = None
    r = s.get('https://www.hackerrank.com/login')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            csrf = re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)
            break
    csrfDict = {'X-CSRF-TOKEN': csrf}
    payload = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    return s.post('https://www.hackerrank.com/auth/login', data=payload, headers=csrfDict)

def logout(s):
    return s.delete('https://www.hackerrank.com/auth/logout')

def getModelGenerator(s, batchSize = -1):
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped?limit=0')
    print(r.text)
    total = r.json()['total']
    if batchSize <= 0:
        batchSize = total

    offset = 0
    while offset < total:
        submissions = getSubmissionsByChallengeGrouped(s, offset, 3) #batchSize)
        offset += batchSize
        challenges = getChallenges(s, submissions.keys())
        submissions = getSubmissions(s, functools.reduce(itertools.chain, submissions.values(), []))
        yield (challenges, submissions)

def getSubmissionsByChallengeGrouped(s, offset, limit):
    params = {'offset':offset, 'limit':limit}
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped', params=params)
    submissions = {}
    for subs in [m['submissions'] for m in r.json()["models"]]:
        id = subs[0]["challenge_id"]
        submissions[id] = [s['id'] for s in subs]
    return submissions

def getChallenges(s, challengeIds):
    challenges = {}
    for id in challengeIds:
        r = s.get('https://www.hackerrank.com/rest/contests/master/challenges/' + str(id))
        j = r.json()
        challenges[id] = {}
    print("Challenges")
    print(challenges.keys())
    return challenges

def getSubmissions(s, submissionIds):
    submissions = {}
    for id in submissionIds:
        r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/' + str(id))
        j = r.json()
        submissions[id] = {}
    print("Submissions")
    print(submissions.keys())
    return submissions

def main():
    # get args and validate
    parser = getArgParser()
    args = parser.parse_args()
    if not args.username or not args.password:
        parser.print_help()
        exit(123)

    submissions = None

    # do site interaction
    s = Session()
    login(s, args.username, args.password)
    models = getModelGenerator(s)

    #makedirs("./hrdir")
    #chdir("./hrdir")

    for (challenges, submissions) in models:
        pass

    # submissions will have to be sorted by time when written to git repo... uh oh

    logout(s)

main()
