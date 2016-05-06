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
    models = getAllModels(s)
    user = getUserModel(s)
    assets = getAssets(s)
    logout(s, csrfHeader)
    return {'models': models, 'user': user, 'assets': assets}

def getAllModels(s):
    contests = {}
    for contestSlug in getContestSlugs(s):
        contest = {}
        url = HR_REST + CONTESTS + '/' + contestSlug
        contest['model'] = getModel(s, url)
        contest['challenges'] = getModelsKeyed(s, url + CHALLENGES, getChallengeSlugs(s, url))
        contest['submissions'] = getModelsKeyed(s, url + SUBMISSIONS, getSubmissionIds(s, url))
        contests[slug] = contest
    return contests

def getLatestData(username, password, data):
    (s, csrfHeader) = login(username, password)
    models = getLatestModels(s, data)
    logout(s, csrfHeader)
    return {'models': models}

def getLatestModels(s, data)
    contests = {}
    for (slug, contest) in data['models'].items():
        url = HR_REST + CONTESTS + slug
        submissionIds = getSubmissionIds(s, url)
        submissionDiff = set(submissionIds) - contest['submissions'].keys()
        getModelsKeyed(s, url + SUBMISSIONS, submissionDiff)

    logout(s, csrfHeader)
    return {'models': models}

def getLatestModels(s, contestData):
    url = HR_REST + CONTESTS + contestData['slug'] + SUBMISSIONS
    submissionIds = getSubmissionIds(s, contestData['slug'])
    if len(contestData['submissions']) == len(submissionIds):
        return []
    return getModelRange(s, url, 0, len(submissionIds) - len(contestData['submissions']))

def getContestSlugs(s):
    url = HR_REST + '/hackers/me/myrank_contests?limit=100&type=recent'
    return ['master'] + [c['slug'] for c in getModels(s, url)]

def getChallengeSlugs(s, url):
    url += '/' + CHALLENGES
    return [c['slug'] for c in getModels(s, url)]

#def getChallenges(s, url, challengeSlugs):
#    url += '/' + CHALLENGES
#    challenges = {}
#    for slug in challengeSlugs:
#        challenges[slug] = getModel(s, url + '/' + slug)
#    return challenges

def getSubmissionIds(s, url):
    url += SUBMISSIONS
    return [s['id'] for s in getModels(s, url)]

#def getSubmissions(s, contestSlug, submissionIds):
#    url += SUBMISSIONS
#    submissions = {}
#    for i in submissionIds:
#        submissions[i] = getModel(s, url + '/' + str(i))
#    return submissions

def getModelsKeyed(s, url, param, ids):
    return {i: getModel(s, url + '/' + i) for i in ids}

def getModel(s, url):
    return s.get(url).json()['model']

def getModels(s, url):
    r = s.get(url).json()
    return r['models'] + getModelRange(s, url, len(r['models']), r['total'])

def getModelRange(s, url, start, end):
    if start >= end:
        return []
    return s.get(url, params={'offset': start, 'limit': end}).json()['models']

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
    return getModels(s, HR_REST + CONTESTS + '/master/hackers/me')

def getAssets(s):
    pass

# OLD

#def getContests(s):
#    url = HR_REST + '/hackers/me/myrank_contests?limit=100&type=recent'
#    contests = {}
#    for c in ['master'] + getModels(s, url):
#        contests[c['slug']] = getModel(s, HR_REST + CONTESTS + c['slug'])
#    contests = {c['slug']:{'model':getModels(s, HR_REST + CONTESTS + c['slug'])} for c in ['master'] + getModels(s, url)}
#    return contests

#def getSubmissions(s, contestSlug, submissionIds):
#    url = HR_REST + CONTESTS + contestSlug + SUBMISSIONS
#    submissions = {sub['id']:getModels(s, url + '/' + str(sub['id'])) for sub in getModels(s, url)}
#    return submissions

def getModelsProcedural(s):
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

