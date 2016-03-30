"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)

 Relevant Links:
 https://www.hackerrank.com/rest/contests/master/submissions/grouped?offset=0limit=2
 https://www.hackerrank.com/rest/hackers/{username}/recent_challenges?offset=0&limit=2
 https://www.hackerrank.com/rest/contests/master/challenges?limit=132352
 https://www.hackerrank.com/rest/contests/master/challenges/{slug or challengeId}
 https://www.hackerrank.com/rest/contests/master/submissions/{submissionId}
 https://www.hackerrank.com/rest/contests/master/challenges/{slug}/submissions/?offset=0&limit=10
"""
import argparse
import pickle
import re
import os.path
from itertools import chain
from requests import Session
from gitops import archiveModel

def getArgParser():
    parser = argparse.ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-u', '--username', action='store', metavar='username', help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', help='account password')
    parser.add_argument('-f', '--file', action='store', metavar='file', help='create/use pickle file')
    parser.add_argument('-d', '--dir', action='store', metavar='dir', help='path repository path')
    parser.add_argument('-b', '--batch', action='store', metavar='batch', type=int, help='challenge request batch size')
    #parser.add_argument('-l', '--load', action='store_true', metavar='load', help='load pickle file')
    #parser.add_argument('-c', '--create', action='store_true', metavar='create', help='create pickle file')
    return parser;

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

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
        ids[c_id] = [s['id'] for s in subs]
    return ids

def getChallenges(s, challengeIds):
    challenges = {}
    for c_id in challengeIds:
        print('  challenge ' + str(c_id))
        r = s.get('https://www.hackerrank.com/rest/contests/master/challenges/' + str(c_id))
        if not r.text:
            print('    --RESPONSE IS EMPTY. SKIPPING.')
            continue
        challenges[c_id] = r.json()['model']
    return challenges

def getSubmissions(s, submissionIds):
    submissions = {}
    for s_id in submissionIds:
        print('    submission ' + str(s_id))
        r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/' + str(s_id))
        if not r.text:
            print('    --RESPONSE IS EMPTY. SKIPPING.')
            continue
        submissions[s_id] = r.json()['model']
    return submissions

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

def main():
    # get args and validate
    parser = getArgParser()
    args = parser.parse_args()
    if not args.username or not args.password:
        parser.print_help()
        exit(123)

    models = None
    if args.file and os.path.exists(args.file):
        models = pickle.load(open(args.file, 'rb'))
    else:
        models = getModelsFromHackerRank(Session(), args.username, args.password, args.batch)

    if args.file and not os.path.exists(args.file):
        pickle.dump(models, open(args.file, 'wb'))

    archiveModel(args.dir, models)

main()
