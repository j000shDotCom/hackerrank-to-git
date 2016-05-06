"""
 All HackerRank specific logic
"""

import re
from requests import Session

HR = 'https://www.hackerrank.com'
HR_REST = HR + '/rest'
CONTESTS = '/contests'
CHALLENGES = '/challenges'
SUBMISSIONS = '/submissions'
SUBMISSIONS_GROUPED = SUBMISSIONS + '/grouped'

def getAllData(username, password):
    (s, csrfHeader) = login(username, password)
    user = getUserModel(s)
    assets = getAssets(s)
    models = getAllModels(s)
    logout(s, csrfHeader)
    return {'models': models, 'user': user, 'assets': assets}

def getAllModels(s):
    contests = {}
    for slug in getContestSlugs(s):
        print()
        print(slug)
        contest = {}
        url = HR_REST + CONTESTS + '/' + slug
        contest['model'] = getModel(s, url)
        contest['challenges'] = getModelsKeyed(s, url + CHALLENGES, getChallengeSlugs(s, url))
        contest['submissions'] = getModelsKeyed(s, url + SUBMISSIONS, getSubmissionIds(s, url))
        contests[slug] = contest
    return contests

def getLatestData(username, password, data):
    (s, csrfHeader) = login(username, password)
    models = getLatestModels(s, data['models'])
    logout(s, csrfHeader)
    return {'models': models}

def getLatestModels(s, models):
    contests = {}
    for slug in getContestSlugs(s):
        print()
        print(slug)
        url = HR_REST + CONTESTS + '/' + slug
        contest = {}
        submissionIds = getSubmissionIds(s, url)
        submissionIdDiff = None
        if slug not in models:
            submissionIdDiff = submissionIds
            contest['model'] = getModel(s, url)
        else:
            submissionIdDiff = submissionIds - models[slug]['submissions'].keys()

        contest['submissions'] = getModelsKeyed(s, url + SUBMISSIONS, submissionIdDiff)
        challengeSlugs = {sub['challenge_slug'] for sub in contest['submissions'].values()}
        contest['challenges'] = getModelsKeyed(s, url + CHALLENGES, challengeSlugs)
        contests[slug] = contest
    return contests

def getContestSlugs(s):
    url = HR_REST + '/hackers/me/myrank_contests?limit=100&type=recent'
    return {'master'} | {c['slug'] for c in getModels(s, url)}

def getChallengeSlugs(s, url):
    url += CHALLENGES
    return {c['slug'] for c in getModels(s, url)}

def getSubmissionIds(s, url):
    url += SUBMISSIONS
    return {s['id'] for s in getModels(s, url)}

def getModelsKeyed(s, url, ids):
    print(ids)
    return {i: getModel(s, url + '/' + str(i)) for i in ids}

def getModel(s, url):
    print(url)
    r = s.get(url)
    if not r:
        print('REQUEST FAILED: ', r.status_code)
        return {}
    return r.json()['model']

def getModels(s, url):
    print(url)
    r = s.get(url)
    if not r:
        print('REQUEST FAILED: ', r.status_code)
        return {}
    r = r.json()
    return r['models'] + getModelRange(s, url, len(r['models']), r['total'])

def getModelRange(s, url, start, end):
    if start >= end:
        return []
    r = s.get(url, params={'offset': start, 'limit': end})
    if not r:
        print('REQUEST FAILED: ', r.status_code)
        return {}
    return r.json()['models']

def login(username, password):
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    s = Session()
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s.post(HR + '/auth/login', data=data, headers=csrfHeader)
    return (s, csrfHeader)

def logout(s, csrfHeader):
    s.delete(HR + '/auth/logout', headers=csrfHeader)

def getCsrfToken(s):
    r = s.get(HR)
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)
    raise Exception('cannot get CSRF token')

def getUserModel(s):
    return getModel(s, HR_REST + CONTESTS + '/master/hackers/me')

def getAssets(s):
    return []

