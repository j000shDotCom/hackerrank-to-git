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

def getNewModels(s, models):
    if not models:
        models = {}
    print('retrieving latest models')
    contests = {}
    for slug in getContestSlugs(s):
        print('\n', slug)
        url = HR_REST + CONTESTS + '/' + slug
        submissionIds = getSubmissionIds(s, url)
        if slug in models and 'submissions' in models[slug]:
            submissionIds -= models[slug]['submissions'].keys()
        if not submissionIds:
            continue
        contest = {}
        contest['model'] = getModel(s, url)
        contest['submissions'] = getModelsKeyed(s, url + SUBMISSIONS, submissionIds)
        challengeSlugs = {sub['challenge_slug'] for sub in contest['submissions'].values()}
        contest['challenges'] = getModelsKeyed(s, url + CHALLENGES, challengeSlugs)
        contests[slug] = contest
    return contests

def mergeModels(models, newModels):
    if not newModels:
        return models or {}
    if not models:
        return newModels or {}
    for slug in newModels.keys():
        if slug not in models:
            models[slug] = newModels[slug]
            continue
        old = models[slug]
        new = newModels[slug]
        old['model'] = new['model']
        old['challenges'].update(new['challenges'])
        old['submissions'].update(new['submissions'])
    return models

def sortModels(contests):
    models = dict()
    for co in contests.values():
        models[co['model']['created_at']] = (co, 'co')
        for ch in co['challenges'].values():
            models[ch['created_at']] = (ch, 'ch')
        for s in co['submissions'].values():
            models[s['created_at']] = (s, 'sub')
    return models

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
    r = s.get(url)
    if not r:
        print('REQUEST FAILED: ', r.status_code, url)
        return {}
    return r.json()['model']

def getModels(s, url):
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

