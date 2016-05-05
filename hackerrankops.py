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
    models = getAllModels(s)
    user = getUserModel(s)
    assets = getAssets(s)
    logout(s, csrfHeader)
    return {'models': models, 'user': user, 'assets': assets}

def getAllModels(s):
    contests = getContests(s)
    for (contestSlug, contest) in contests.items():
        contest['challenges'] = getChallenges(s, contestSlug)
        contest['submissions'] = getSubmissions(s, contestSlug)
    return contests

def getNewModels(username, password, data):
    models = {}
    (s, csrfHeader) = login(username, password)
    for (contestSlug, contestData) in data['models'].items():
        latest = getLatestContestData(s, contestData)
        models[contestSlug] = latest
    logout(s, csrfHeader)
    return models

def getLatestContestData(s, contestData):
    url = HR_REST + CONTESTS + contestData['slug'] + SUBMISSIONS
    submissions = getSubmissionIds(s, contestData['slug'])
    if len(contestData['submissions']) == len(submissions):
        return []
    # TODO get submission models by IDs
    newSubmissions = getModelRange(s, url, 0, numSubmissionsNow - len(contestData['submissions'])
    return newSubmissions

def getContests(s):
    url = HR_REST + '/hackers/me/myrank_contests?limit=100&type=recent'
    contests = {c['slug']:{'model':getModels(s, HR_REST + CONTESTS + c['slug'])} for c in ['master'] + getModels(s, url)}
    return contests

def getChallengeSlugs(s, contestSlug):
    url = HR_REST + CONTESTS + contestSlug + CHALLENGES
    return [c['slug'] for c in getModels(s, url)]

def getChallenges(s, contestSlug):
    url = HR_REST + CONTESTS + contestSlug + CHALLENGES
    challenges = {c['slug']:getModels(s, url + '/' + c['slug']) for c in getModels(s, url)}
    return challenges

def getSubmissionIds(s, contestSlug):
    url = HR_REST + CONTESTS + contestSlug + SUBMISSIONS
    return [s['id'] for s in getModels(s, url)]

def getSubmissions(s, contestSlug):
    url = HR_REST + CONTESTS + contestSlug + SUBMISSIONS
    submissions = {sub['id']:getModels(s, url + '/' + str(sub['id'])) for sub in getModels(s, url)}
    return submissions

def getModelsForIds(s, urlSlug, param, ids):
    return [i[param]: getModels(s, url + '/' + urlSlug + '/' + i) for i in ids]

def getModels(s, url):
    r = s.get(url).json()
    if ('model' in r):
        return r['model']
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
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s = Session()
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

