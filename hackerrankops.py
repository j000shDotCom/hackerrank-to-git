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
        newSubmissions = getNewSubmissions(s, contestSlug, data['models'][contestSlug]['submissions'])
        contestData['newSubmissions'] = newSubmissions
    logout(s, csrfHeader)
    return data

def getNewSubmissions(s, contestSlug, contestSubmissions):
    numSubmissions = getNumModels(s, url)
    if len(contestData['submissions']) == numSubmissions:
        return contestData
    else
        newSubmissions =

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

def getModels(s):
    contests = {}
    url = 'https://www.hackerrank.com/rest/hackers/me/myrank_contests?limit=100&type=recent'
    contests = getAllModels(s, url, ['master'])
    #url = 'https://www.hackerrank.com/rest/hackers/me/contest_participation'
    #contestSlugs = ['master'] + [m['slug'] for m in getAllModels(s, url)]
    for contestSlug in contestSlugs:
        # contest model
        url = 'https://www.hackerrank.com/rest/contests/' + contestSlug
        contests[contestSlug] = s.get(url).json()['model']
        print(contestSlug)

        url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/'
        submissions = getAllModels(s, url)
        challengeSlugs = {s['challenge']['slug'] for s in submissions}

        # challenge models
        contests[contestSlug]['challenges'] = {}
        for challengeSlug in challengeSlugs:
            url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/challenges/' + challengeSlug
            contests[contestSlug]['challenges'][challengeSlug] = s.get(url).json()['model']
            print(challengeSlug)

        # submission models
        contests[contestSlug]['submissions'] = {}
        for submission in submissions:
            url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/' + str(submission['id'])
            contests[contestSlug]['submissions'][submission['id']] = s.get(url).json()['model']
            print(submission['id'])
        print()

    return contests

def getNumModels(s, url):
    r = s.get(url).json()
    return (r['total'], r['models'])

def getAllModels(s, url):
    (total, lst) = getNumModels(s, url)
    if len(lst) < total:
        lst += s.get(url, params={'offset':len(lst), 'limit':total}).json()['models']
    return lst

