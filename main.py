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
import os.path
from requests import Request, Session
from requests.utils import add_dict_to_cookiejar, dict_from_cookiejar
from os import makedirs


def getArgParser():
    parser = argparse.ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-l', '--local', action='store', type=bool, metavar='local', help='local git repo')
    parser.add_argument('-r', '--remote', action='store', type=str, metavar='remote', help='remote git repo URL')
    parser.add_argument('-f', '--file', action='store', type=bool, metavar='file', help='parse HAR file')
    parser.add_argument('-c', '--config', metavar='config')
    parser.add_argument('-d', '--daemon', action='store_true', default=False, help='run in background')
    parser.add_argument('-u', '--username', action='store', metavar='username', help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', help='account password')
    return parser;

def parseConfigFile(config):
    # primarily get username and password from config file
    # NOTE: ensure config file is included in .gitignore
    pass

def addCookies(s, cookies):
    s.cookies = add_dict_to_cookiejar(s.cookies, cookies)

def login(s, username, password):
    payload = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrf = None
    r = s.get('https://www.hackerrank.com/login')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            csrf = re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)
            break
    csrfDict = {'X-CSRF-TOKEN': csrf}
    r = s.post('https://www.hackerrank.com/auth/login', data=payload, headers=csrfDict)
    return r.status_code

def getSubmissions(s, batchSize = -1):
    # get total submission count
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped?limit=0')
    total = r.json()['total']
    print(r.text)
    if batchSize <= 0:
        batchSize = total

    offset = 0
    while offset < total:
        submissions = getSubmissionsByChallenge(s, offset, 10) # batchSize)
        offset += batchSize
        challenges = getChallenges(submissions.keys())
        submissions = getSubmissions(submissions.values())
    return None

def getChallenges(challengeIds):
    pass

def getSubmissions(submissionIds):
    pass

def getSubmissionsByChallenge(s, offset, limit):
    params = {'offset':offset, 'limit':limit}
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped', params = params)
    submissions = {}
    for subs in [model['submissions'] for model in r.json()["models"]]:
        submissions[subs[0]["challenge_id"]] = [s['id'] for s in subs]
    return submissions

def logout(s):
    r = s.delete('https://www.hackerrank.com/auth/logout')
    pass

def main():
    # get config
    parser = getArgParser()
    args = parser.parse_args()
    if args.config:
        args = parseConfigFile(args.config)

    if not args.username or not args.password:
        parser.print_help()
        exit(123)

    submissions = None

    # do site interaction
    s = Session()
    login(s, args.username, args.password)
    submissions = getSubmissions(s)
    logout(s)

    if not submissions:
        pass

    # TODO build git repo
    #if args.local:
    #    makedirs(args.local)
    #if args.remote:

main()
