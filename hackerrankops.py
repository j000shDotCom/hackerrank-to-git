"""
  All HackerRank specific logic
"""

import re
import os.path
from itertools import chain

def getHackerRankData(s, username, password, batchSize=-1):
    print('LOGGING IN AS ' + username)
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrfHeader = {'X-CSRF-TOKEN': getCsrfToken(s)}
    s.post('https://www.hackerrank.com/auth/login', data=data, headers=csrfHeader)
    user = s.get("https://www.hackerrank.com/rest/contests/master/hackers/me").json()['model']
    return {'models': getModelGenerator(s, batchSize, csrfHeader), 'user': user}

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

def getModelGenerator(s, batchSize, csrfHeader):
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
        submissions = getSubmissions(s, chain.from_iterable(ids.values()))
        yield (ids, challenges, submissions)
        break

    print('LOGGING OUT')
    s.delete('https://www.hackerrank.com/auth/logout', headers=csrfHeader)

def getSubmissionsByChallengeGrouped(s, offset, limit):
    params = {'offset':offset, 'limit':limit}
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped', params=params)
    ids = {}
    for subs in [m['submissions'] for m in r.json()["models"]]:
        c_id = subs[0]["challenge_id"]
        ids[c_id] = [s['id'] for s in subs]
    return ids

def getChallenges(s, challengeIds):
    challenges = {}
    for c_id in challengeIds:
        print('  chal ' + str(c_id))
        r = s.get('https://www.hackerrank.com/rest/contests/master/challenges/' + str(c_id))
        if not r.text:
            print('    --RESPONSE IS EMPTY. SKIPPING.') #TODO
            continue
        challenges[c_id] = r.json()['model']
    return challenges

def getSubmissions(s, submissionIds):
    submissions = {}
    for s_id in submissionIds:
        print('  sub ' + str(s_id))
        r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/' + str(s_id))
        if not r.text:
            print('    --RESPONSE IS EMPTY. SKIPPING.') #TODO
            continue
        submissions[s_id] = r.json()['model']
    return submissions

