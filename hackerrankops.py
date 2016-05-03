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

HR = 'https://www.hackerrank.com'
HR_REST = HR + '/rest'
CONTESTS = '/contests'
CHALLENGES = '/challenges'
SUBMISSIONS = '/submissions'
SUBMISSIONS_GROUPED = SUBMISSIONS + '/grouped'

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
    url = HR_REST + CONTESTS + contestSlug + SUBMISSIONS
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
    s.post(HR + '/auth/login', data=data, headers=csrfHeader)
    return (s, csrfHeader)

def logout(s, csrfHeader):
    s.delete(HR + '/auth/logout', headers=csrfHeader)

# TODO get assets and CSRF token in the same request
def getCsrfToken(s):
    r = s.get(HR)
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)
    raise Exception('cannot get CSRF token')

def getUserModel(s):
    return s.get(HR_REST + CONTESTS + '/master/hackers/me').json()['model']

def getContests(s):
    url = HR_REST + '/hackers/me/myrank_contests?limit=100&type=recent'
    contests = {c['slug']:dict() for c in ['master'] + getAllModels(s, url)}
    url = HR_REST + CONTESTS + contest['slug']
    contest['model'] = s.get(url).json()['model']
    return contests

def getSubmissions(s, contestSlug):
    url = HR_REST + CONTESTS + contestSlug + SUBMISSIONS
    submissions = {sub['id']:getById(s, contestSlug, sub['id']) for sub in getAllModels(s, url)}
    return submissions

#def getById(s, contestSlug, sId):
#    url = HR_REST + CONTESTS + contestSlug + SUBMISSIONS + str(submission['id'])
#    return getAllModels(s, url)

def getModels(s):
    contests = getContests(s)
    for (contestSlug, contest) in contests.items():

        # submissions overview
        url = HR_REST + CONTESTS + contestSlug + SUBMISSIONS
        submissions = getAllModels(s, url)
        contest['submissions'] = {}
        challengeSlugs = {s['challenge']['slug'] for s in submissions}

        # challenge models
        contests[contestSlug]['challenges'] = {}
        for challengeSlug in challengeSlugs:
            url = HR_REST + CONTESTS + contestSlug + CHALLENGES + challengeSlug
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

