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
    print('LOGGING IN AS ' + username)
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s.post('https://www.hackerrank.com/auth/login', data=data, headers=csrfHeader)
    user = s.get("https://www.hackerrank.com/rest/contests/master/hackers/me").json()['model']
    return {'models': getModelGenerator(s, csrfHeader), 'user': user}

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

def getModelGenerator(s, csrfHeader, grouped):
    # get submissions to master contest
    url = 'https://www.hackerrank.com/rest/contests/master/submissions' + ('/grouped' if grouped else '')
    total = s.get(url, params={limit:0}).json()['total']
    offset = 0
    while offset < total:
        print('fetching batch [{}-{}] of {}'.format(offset, offset + 10, total))
        ids = getSubmissionsByChallenge(s, offset, grouped)
        offset += batchSize
        challenges = getModelsOfType(s, "challenges", ids.keys())
        submissions = getModelsOfType(s, "submissions", chain.from_iterable(ids.values()))
        yield (ids, challenges, submissions)

    print('LOGGING OUT')
    s.delete('https://www.hackerrank.com/auth/logout', headers=csrfHeader)

def getSubmissionsByContest(s, contest):
    r = s.get('https://www.hackerrank.com/rest/hackers/jlindsay90/contest_participation')

def getSubmissionsByChallenge(s, offset, limit):
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

def getModelsOfType(s, modelType modelIds):
    models = {}
    for modelId in modelIds:
        r = s.get('https://www.hackerrank.com/rest/contests/master/{}/{}'.format(modelType, modelId))
        if not r.text:
            print('    --RESPONSE IS EMPTY. SKIPPING.') #TODO
            continue
        challenges[c_id] = r.json()['model']
    return challenges

