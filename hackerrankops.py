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
    models = getAllModels(s)
    logout(s, csrfHeader)
    return {'models': models, 'user': user}

def getAllModels(s):
    contests = {}
    for slug in getContestSlugs(s):
        print('\n', slug)
        url = HR_REST + CONTESTS + '/' + slug
        contest = {}
        contest['model'] = getModel(s, url)
        contest['challenges'] = getModelsKeyed(s, url + CHALLENGES, getChallengeSlugs(s, url))
        contest['submissions'] = getModelsKeyed(s, url + SUBMISSIONS, getSubmissionIds(s, url))
        contests[slug] = contest
    return contests

def getNewData(username, password, data):
    (s, csrfHeader) = login(username, password)
    models = getLatestModels(s, data['models'])
    logout(s, csrfHeader)
    return {'models': models, 'user': data['user']}

def getLatestModels(s, models):
    print('checking for latest models')
    contests = {}
    for slug in getContestSlugs(s):
        print('\n', slug)
        submissionIds = getSubmissionIds(s, url)
        if slug in models:
            submissionIds -= models[slug]['submissions'].keys()
        if not submissionIds:
            continue
        url = HR_REST + CONTESTS + '/' + slug
        contest = {}
        contest['model'] = getModel(s, url)
        contest['submissions'] = getModelsKeyed(s, url + SUBMISSIONS, submissionIds)
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
    models = {}
    for i in ids:
        model = getModel(s, url + '/' + str(i))
        if not model:
            continue
        models[i] = model
    return models

def getModel(s, url):
    #print(url)
    r = s.get(url)
    if not r:
        print('REQUEST FAILED: ', r.status_code, url)
        return {}
    return r.json()['model']

def getModels(s, url):
    #print(url)
    r = s.get(url)
    if not r:
        print('REQUEST FAILED: ', r.status_code, url)
        return {}
    r = r.json()
    return r['models'] + getModelRange(s, url, len(r['models']), r['total'])

def getModelRange(s, url, start, end):
    if start >= end:
        return []
    r = s.get(url, params={'offset': start, 'limit': end})
    if not r:
        print('REQUEST FAILED: ', r.status_code, url)
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

