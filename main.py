"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)

 Relevant Links:
 https://www.hackerrank.com/rest/contests/master/submissions/grouped?offset=0limit=2
 https://www.hackerrank.com/rest/hackers/{username}/recent_challenges?offset=0&limit=2
 https://www.hackerrank.com/rest/contests/master/challenges/{slug or challengeId}
 https://www.hackerrank.com/rest/contests/master/submissions/{submissionId}
 https://www.hackerrank.com/rest/contests/master/challenges/{slug}/submissions/?offset=0&limit=10
"""
import argparse
import os
import pickle
import re
from functools import reduce
from itertools import chain
from requests import Request, Session
from sh import git

def getArgParser():
    parser = argparse.ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-u', '--username', action='store', metavar='username', help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', help='account password')
    parser.add_argument('-f', '--file', action='store', metavar='file', help='create/use pickle file')
    parser.add_argument('-d', '--dir', action='store', metavar='dir', help='path repository path')
    return parser;

def getCsrfToken(s):
    r = s.get('https://www.hackerrank.com/')
    for line in r.text.split("\n"):
        if ('csrf-token' in line):
            return re.sub(r"<meta content=\"([^\"]+)\".*", r"\1", line)

def login(s, username, password, csrfToken):
    data = {
        'login' : username,
        'password' : password,
        'remember_me' : 'false',
    }
    csrfHeader = {'X-CSRF-TOKEN': csrfToken}
    print('logging in. ', csrfHeader)
    return s.post('https://www.hackerrank.com/auth/login', data=data, headers=csrfHeader)

def getModelGenerator(s, batchSize = -1):
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped?limit=0')
    total = r.json()['total']
    if batchSize <= 0:
        batchSize = total

    offset = 0
    while offset < total:
        idGroups = getSubmissionsByChallengeGrouped(s, offset, batchSize)
        offset += batchSize
        challenges = getChallenges(s, idGroups.keys())
        submissions = getSubmissions(s, reduce(chain, idGroups.values(), []))
        yield {'id_groups':idGroups, 'challenges':challenges, 'submissions':submissions}

def getSubmissionsByChallengeGrouped(s, offset, limit):
    params = {'offset':offset, 'limit':limit}
    print('getting submission batch ', params)
    r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/grouped', params=params)
    submissions = {}
    for subs in [m['submissions'] for m in r.json()["models"]]:
        c_id = subs[0]["challenge_id"]
        submissions[c_id] = [s['id'] for s in subs].sort(lambda s: int(s['created_at_epoch']))
    return submissions

def getChallenges(s, challengeIds):
    print('requesting challenges ', challengeIds)
    challenges = {}
    for c_id in challengeIds:
        r = s.get('https://www.hackerrank.com/rest/contests/master/challenges/' + str(c_id))
        challenges[c_id] = r.json()['model']
    return challenges

def getSubmissions(s, submissionIds):
    print('requesting submissions ', submissionIds)
    submissions = {}
    for s_id in submissionIds:
        r = s.get('https://www.hackerrank.com/rest/contests/master/submissions/' + str(s_id))
        submissions[s_id] = r.json()['model']
    return submissions

def writeChallenge(challenge):
    filename = challenge['slug'] + '.html'
    print('generating ' + filename)
    with open(filename, 'w') as f:
        f.write('<!DOCTYPE html><html><head><script type="text/javascript" async ' \
            + 'src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML">' \
            + '</script></head><body>\n')
        f.write(challenge['body_html'])
        f.write('\n</body></html>\n')
    git.add(filename)
    git.commit(m='added challenge ' + filename)

def writeSubmissions(submissions):
    print('inserting submission ' + submissions[0]['challenge_slug'])
    for sub in submissions:
        filename = sub['challenge_slug'] + getFileExtension(sub)
        with open(filename, 'w') as f:
            f.write(sub['code'])
        git.add(filename)
        git.commit(m="{} ({}) {} {}".format(
            sub['name'], sub['language'], getFrac(sub['testcase_status']), sub['status']),
            _ok_code=[0,1])

def getFileExtension(submission):
    if submission['kind'] != 'code':
        return '.txt'
    lang = submission['language']
    if lang == 'java' or lang == 'java8':
        return '.java'
    if lang == 'haskell':
        return '.hs'
    if lang == 'prolog' or lang == 'perl':
        return '.pl'
    return '.txt'

def initializeDir(path):
    if not os.exists(path):
        makedirs(path)
    chdir(path)
    git.init()
    with open('README', 'w') as f:
        f.write('dummy README file to make a commit\n') #TODO
    git.add('README')
    git.commit(m='initial commit')

def archiveModel(model_obj):
    idGroups = model_obj['id_groups']
    challenges = model_obj['challenges']
    submissions = model_obj['submissions']
    for c_id in challenges:
        challenge = challenges[c_id]
        subs = [submissions[s_id] for s_id in idGroups[c_id]]
        git.checkout(b=challenge['slug'])
        writeChallenge(challenge)
        writeSubmissions(subs)
        git.checkout('master')

def getFrac(testcases):
    return '[{}/{}]'.format(sum(testcases), len(testcases))

def logout(s, csrfToken):
    return s.delete('https://www.hackerrank.com/auth/logout', headers=csrfToken)

def getModelsFromHackerRank(s, username, password):
    csrf = getCsrfToken(s)
    login(s, username, password, csrf)
    ids = {}
    challenges = {}
    submissions = {}
    for model in getModelGenerator(s, 5):
        ids.update(model['id_groups'])
        challenges.update(model['challenges'])
        submissions.update(model['submissions'])
    logout(s, csrf)
    return {'id_groups':ids, 'challenges':challenges, 'submissions':submissions}

def main():
    # get args and validate
    parser = getArgParser()
    args = parser.parse_args()
    if not args.username or not args.password:
        parser.print_help()
        exit(123)

    models = None
    if args.file and os.path.exists(args.file):
        models = pickle.load(open(args.file), 'rb')
    else:
        models = getModelsFromHackerRank(Session(), args.username, args.password)

    if args.file and not os.path.exists(args.file):
        pickle.dump(models, open(args.file), 'wb')

    initializeDir(args.path)
    for model in models:
        archiveModel(model)

main()
