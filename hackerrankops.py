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
from requests import Session

def getHackerRankData(username, password):
    (s, csrfHeader) = login(username, password)
    models = getModels(s)
    user = getUserModel(s)
    assets = getAssets(s)
    logout(s, csrfHeader)
    return {'models': models, 'user': user, 'assets': assets}

def getAllNewSubmissions(username, password, data):
    models = {}
    (s, csrfHeader) = login(username, password)
    for (contestSlug, contestData) in data['models'].items():
        newSubmissions = getNewContestSubmissions(s, contestSlug, data['models'][contestSlug]['submissions'])
        contestData['newSubmissions'] = newSubmissions
    logout(s, csrfHeader)
    return data

def getNewContestSubmissions(s, contestSlug, contestData):
    url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/'
    numSubmissions = contestDate['submissions']
    numSubmissionsNow = getNumModels(s, url)
    if len(contestData['submissions']) != numSubmissionsNow:
        newSubmissions = getModelRange(s, url, 0, numSubmissionsNow - numSubmissions)
        print(newSubmissions)
        return newSubmissions

def login(username, password):
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s = Session()
    s.post('https://www.hackerrank.com/auth/login', data=data, headers=csrfHeader)
    return (s, csrfHeader)

def logout(s, csrfHeader):
    s.delete('https://www.hackerrank.com/auth/logout', headers=csrfHeader)

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

def getUserModel(s):
    return s.get('https://www.hackerrank.com/rest/contests/master/hackers/me').json()['model']

def getAssets(s):
    pass

def getContests(s):
    url = 'https://www.hackerrank.com/rest/hackers/me/myrank_contests?limit=100&type=recent'
    # url = 'https://www.hackerrank.com/rest/hackers/me/contest_participation'
    contests = {c['slug']:dict() for c in ['master'] + getAllModels(s, url)}
    url = 'https://www.hackerrank.com/rest/contests/' + contest['slug']
    contest['model'] = s.get(url).json()['model']
    return contests

def getSubmissions(s, contestSlug):
    url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/'
    submissions = {sub['id']:getById(s, contestSlug, sub['id']) for sub in getAllModels(s, url)}

def getById(s, contestSlug, sId):
    url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/' + str(submission['id'])
    return getAllModels(s, url)

def getModels(s):
    contests = getContests(s)
    for (contestSlug, contest) in contests.items():

        # submissions overview
        url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/'
        submissions = getAllModels(s, url)
        contest['submissions'] = {}
        challengeSlugs = {s['challenge']['slug'] for s in submissions}

        # challenge models
        contests[contestSlug]['challenges'] = {}
        for challengeSlug in challengeSlugs:
            url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/challenges/' + challengeSlug
            contests[contestSlug]['challenges'][challengeSlug] = getAllModels(s, url)
            print(challengeSlug + ': ' + len(contests[contestSlug]['challenges'][challengeSlug]) + ' challenge models')

        # submission models
        contests[contestSlug]['submissions'] = {}
        for submission in submissions:
            url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/' + str(submission['id'])
            contests[contestSlug]['submissions'][submission['id']] = getAllModels(s, url)
            print(submission['id'] + ': ' + len( contests[contestSlug]['submissions'][submission['id']]))

    return contests

def getNumModels(s, url):
    r = s.get(url).json()
    return (r['total'], r['models'])

def getModelRange(s, url, start, end):
    if start >= end:
        return []
    return s.get(url, params={'offset': start, 'limit': end}).json()['models']

def getAllModels(s, url):
    (total, lst) = getNumModels(s, url)
    lst += getModelRange(s, url, len(lst), total)
    return lst

