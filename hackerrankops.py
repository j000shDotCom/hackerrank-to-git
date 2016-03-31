"""
  All HackerRank specific logic
"""

import re
import os.path
from itertools import chain

def getModelsFromHackerRank(s, username, password, batchSize):
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s.post('https://www.hackerrank.com/auth/login', data=data, headers=csrfHeader)
    ids = {}
    challenges = {}
    submissions = {}
    for model in getModelGenerator(s, batchSize):
        ids.update(model['ids'])
        challenges.update(model['challenges'])
        submissions.update(model['submissions'])
    s.delete('https://www.hackerrank.com/auth/logout', headers=csrfHeader)
    return {'ids':ids, 'challenges':challenges, 'submissions':submissions}

def getModelGenerator(s, batchSize = -1):
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped?limit=0')
    total = r.json()['total']
    if batchSize <= 0:
        batchSize = total

    offset = 0
    while offset < total:
        print('fetching batch [{}-{}] of {}'.format(offset, offset + batchSize, total))
        ids = getSubmissionsByChallengeGrouped(s, offset, batchSize)
        offset += batchSize
        challenges = getChallenges(s, ids.keys())
        submissions = getSubmissions(s, list(chain.from_iterable(ids.values())))
        yield {'ids':ids, 'challenges':challenges, 'submissions':submissions}

def getSubmissionsByChallengeGrouped(s, offset, limit):
    params = {'offset':offset, 'limit':limit}
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped', params=params)
    ids = {}
    for subs in [m['submissions'] for m in r.json()["models"]]:
        c_id = subs[0]["challenge_id"]
        ids[c_id] = sorted([s['id'] for s in subs], reverse=True)
    return ids

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

def getChallenges(s, challengeIds):
    challenges = {}
    for c_id in challengeIds:
        print('  chal ' + str(c_id))
        r = s.get('https://www.hackerrank.com/rest/contests/master/challenges/' + str(c_id))
        if not r.text:
            print('    --RESPONSE IS EMPTY. SKIPPING.')
            continue
        challenges[c_id] = r.json()['model']
    return challenges

def getSubmissions(s, submissionIds):
    submissions = {}
    for s_id in submissionIds:
        print('  sub ' + str(s_id))
        r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/' + str(s_id))
        if not r.text:
            print('    --RESPONSE IS EMPTY. SKIPPING.')
            continue
        submissions[s_id] = r.json()['model']
    return submissions

