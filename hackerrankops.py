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
    s = Session()
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s.post('https://www.hackerrank.com/auth/login', data=data, headers=csrfHeader)
    user = s.get("https://www.hackerrank.com/rest/contests/master/hackers/me").json()['model']
    data = {'models': getModels(s, csrfHeader), 'user': user}
    s.delete('https://www.hackerrank.com/auth/logout', headers=csrfHeader)
    return data

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

def getModels(s, csrfHeader):
    contests = {}
    #url = 'https://www.hackerrank.com/rest/hackers/me/myrank_contests?limit=100&type=recent'
    #contests = getAllModels(s, url2, ['master'])
    url = 'https://www.hackerrank.com/rest/hackers/me/contest_participation'
    contestSlugs = ['master'] + [m['slug'] for m in getAllModels(s, url)]
    for contestSlug in contestSlugs:
        # get contest model
        url = 'https://www.hackerrank.com/rest/contests/' + contestSlug
        contests[contestSlug] = s.get(url).json() # is {model:{}}
        print(contestSlug)

        url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/'
        submissions = getAllModels(s, url)
        challengeSlugs = {s['challenge']['slug'] for s in submissions} # set comprehension

        # get challenge models
        contests[contestSlug]['challenges'] = {}
        for challengeSlug in challengeSlugs:
            url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/challenges/' + challengeSlug
            contests[contestSlug]['challenges'][challengeSlug] = s.get(url).json()['model']
            print(challengeSlug)

        # get submission models
        contests[contestSlug]['submissions'] = {}
        for submission in submissions:
            url = 'https://www.hackerrank.com/rest/contests/' + contestSlug + '/submissions/' + str(submission['id'])
            contests[contestSlug]['submissions'][submission['id']] = s.get(url).json()['model']
            print(submission['id'])

    return contests

def getAllModels(s, url):
    r = s.get(url).json()
    total = r['total']
    lst = r['models']
    if len(r['models']) < total:
        lst += s.get(url, params={'offset':len(r['models']), 'limit':total}).json()['models']
    return lst

