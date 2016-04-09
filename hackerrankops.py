"""
 All HackerRank specific logic

 Relevant Links:
 https://www.hackerrank.com/rest/contests/master/submissions/grouped?offset=0limit=2
 https://www.hackerrank.com/rest/hackers/{username}/recent_challenges?offset=0&limit=2
 https://www.hackerrank.com/rest/contests/master/challenges?limit=132352
 https://www.hackerrank.com/rest/contests/master/challenges/{slug or challengeId}
 https://www.hackerrank.com/rest/contests/master/submissions/{submissionId}
 https://www.hackerrank.com/rest/contests/master/challenges/{slug}/submissions/?offset=0&limit=10
 https://www.hackerrank.com/rest/hackers/jlindsay90/contest_participation?offset=5&limit=5
"""

import re
import os.path
from itertools import chain

def getHackerRankData(s, username, password):
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s.post('https://www.hackerrank.com/auth/login', data=data, headers=csrfHeader)
    user = s.get("https://www.hackerrank.com/rest/contests/master/hackers/me").json()['model']
    data = {'models': getModelGenerator(s, csrfHeader), 'user': user}
    s.delete('https://www.hackerrank.com/auth/logout', headers=csrfHeader)
    return data

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

def getModelGenerator(s, csrfHeader):
    contests = {}
    #url = 'https://www.hackerrank.com/rest/hackers/me/myrank_contests?limit=100&type=recent'
    #contests = getAllModels(s, url2, ['master'])
    url = 'https://www.hackerrank.com/rest/hackers/me/contest_participation'
    contestSlugs = [m['slug'] for m in getAllModels(s, url, ['master'])]
    for contestSlug in contestSlugs:
        # get contest model
        url = 'https://www.hackerrank.com/rest/contests/' + contest
        contests[contestSlug] = s.get(url).json() # is {model:{}}

        # NOTE only queries 5 submissions per challenge
        #url = 'https://www.hackerrank.com/rest/contests/' + contest + '/submissions/grouped'
        #group = getAllModels(s, url)
        #groups += group

        url = 'https://www.hackerrank.com/rest/contests/' + contest + '/submissions/'
        submissions = getAllModels(s, url)
        challenges = {s['challenge'] for s in submissions} # set comprehension ... COOL! <3 Python

        # get challenge models
        contests[contestSlug]['challenges'] = {}
        for challenge in challenges:
            url = 'https://www.hackerrank.com/rest/contests/' + contest + '/challenges/' + challenge['slug']
            contests[contestSlug]['challenges'][chellenge['slug'] = s.get(url).json()['model']

        # get submission models
        contests[contestSlug]['submissions'] = {}
        for submission in submissions:
            url = 'https://www.hackerrank.com/rest/contests/' + contest + '/submissions/' + submission['id']
            contests[contestSlug]['submissions'][submission['id'] = s.get(url).json()['model']

        #yield contests[contestSlug]

    return contests

def getAllModels(s, url, lst = []):
    r = s.get(url).json()
    total = r['total']
    lst += r['models']
    if len(r['models']) < total:
        lst += s.get(url, params={'offset'=len(r['models']), 'limit':total}).json()['models']
    return lst

def getModelsById(s, contest, modelType, modelIds, offset = -1, limit = -1):
    modelsById = {}
    for modelId in modelIds:
        url = 'https://www.hackerrank.com/rest/contests/{}/{}/{}'.format(contest, modelType, modelId)
        r = s.get(url).json()
        models = r['models']
        total = r['total']
        if len(models) < total:
            rest = s.get(url, params={'offset':len(models), 'limit':total}).json()['models']
            models.extend(rest)
    return models

def getChallenges(s, contest, offset = -1, limit = -1):
    url =
    params = {'offset':offset, 'limit':limit}
    r = s.get('https://www.hackerrank.com/rest/contest/master/submissions', params=params)
    submissions = []

def getSubmissionsByChallengeGrouped(s, offset, limit):
    params = {'offset':offset, 'limit':limit}
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped', params=params)
    ids = {}
    for subs in [m['submissions'] for m in r.json()["models"]]:
        c_id = subs[0]["challenge_id"]
        ids[c_id] = [s['id'] for s in subs]
    return ids

