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
    headers = {
        'Host' : 'www.hackerrank.com',
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'en-US,en;q=0.5',
        'Accept-Encoding' : 'gzip, deflate',
        #'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
        #'Content-Type' : 'application/json; charset=utf-8',
        #'X-Requested-With' : 'XMLHttpRequest',
        'Connection' : 'keep-alive',
        'Referer' : 'https://www.hackerrank.com/login',
        #'Cache-Control' : 'max-age=0'
    }
    #s.headers.update(headers)

    payload = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrf = None
    r = s.get('https://www.hackerrank.com/login')
    for line in r.text.split("\n"):
        if ("csrf-token" in line):
            csrf = re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)
            break
    csrfDict = {'X-CSRF-TOKEN': csrf}
    r = s.post('https://www.hackerrank.com/auth/login', data=payload, headers=csrfDict)

    #r = s.get("https://www.hackerrank.com/rest/contests/master/hackers/me?&_=1457459220026")
    #print(r.text)

def getSubmissions(s, batchSize = -1):
    # get total submission count
    # returns '{"models":[],"total":152}'

    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/?limit=0')
    total = r.json()['total']
    print(r.text)
    if batchSize <= 0:
        batchSize = total

    exit()
    # get submissions in batches (useful for slower connections)
    submissionModels = []

    offset = 0
    while offset < total:
        params = {'offset' : offset, 'limit' : 5}
        req = s.get('https://www.hackerrank.com/rest/contests/master/submissions/', params = params)
        submissionModels += req.json()['models']
        offset += batchSize

    # https://www.hackerrank.com/rest/contests/master/challenges/similarpair/submissions/?offset=0&limit=10&_=1454867740795
    for model in submissionModels:
        getSubmissionDetails(model)

def getSubmissionDetails(model):
    print("DETAILS")
    print(model['challenge']['slug'] + ' ' + model['status'])

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
