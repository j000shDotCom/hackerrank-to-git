"""
  This file does all the fancy git operations and file writing
"""
import os
from pickle import load, dump
from bs4 import BeautifulSoup
from sh import git

HR = 'https://www.hackerrank.com'
HR_REST = HR + '/rest'
CONTESTS = '/contests'
CHALLENGES = '/challenges'
SUBMISSIONS = '/submissions'
SUBMISSIONS_GROUPED = SUBMISSIONS + '/grouped'

def loadPickle(filename):
    try:
        return load(open(filename, 'rb'))
    except:
        return None

def dumpPickle(data, filename):
    try:
        dump(data, open(filename, 'wb'))
    except:
        return None

def archiveData(repoPath, data):
    createdDate = data['user']['created_at']
    initializeDir(repoPath, data['user']['name'], data['user']['email'])
    collectSubmissions(data['models'])
    writeData()

def collectSubmissions(contests):
    return [c['submissions'] for c in contests]

def collectChallenges(contest):
    pass

def archiveModels(models):
    for (contestSlug, contest) in models.items():
        archiveModel(contest)
        os.makedirs(contestSlug)
        os.chdir(contestSlug)
        writeContest(contest)
        gitCommitModel(contest)

        for (challengeSlug, challenge) in contest['challenges'].items():
            if challenge:
                writeChallenge(challenge)
        for (submissionId, submission) in sorted(contest['submissions'].items()):
            if submission:
                writeSubmission(submission)

        os.chdir('..')


def initializeDir(path, name, email, repo = None):
    os.makedirs(path)
    os.chdir(path)
    git.init()
    os.chmod(path + '/.git/', 0b111000000)
    git.config('--local', 'user.name', '"' + name + '"')
    git.config('--local', 'user.email', '"' + email + '"')
    if repo:
        git.remote.add('origin', repo)

def writeContest(contest):
    hrurl = HR + CONTESTS + '/' + contest['model']['slug']
    resturl = HR_REST + CONTESTS + '/' + contest['model']['slug']
    challengehtml = '<ul>'
    for (challengeSlug, challenge) in contest['challenges'].items():
        challengehtml += '<li><a href="{}">{}</a></li>'.format(challengeSlug + '.html', challengeSlug)
    challengehtml += '</ul>'
    html = """<!DOCTYPE html>
    <html><head></head><body>
    <h1>{}</h1><a href="{}">Contest</a> <a href="{}">JSON</a><hr/>{}<hr/>
    <h2>Challenges</h2>{}</body></html>
    """.format(contest['model']['name'], hrurl, resturl, contest['model']['description_html'], challengehtml)

    with open('index.html', 'w') as f:
        f.write(BeautifulSoup(html, 'html5lib').prettify() + '\n')
    git.add('index.html')

def writeChallenge(challenge):
    asseturl = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML'
    js = "MathJax.Hub.Config({tex2jax:{inlineMath:[['$','$'],['\\(','\\)']]}});"
    hrurl = HR + \
        + (CONTESTS + '/' + challenge['contest_slug'] if challenge['contest_slug'] != 'master' else '') \
        + CHALLENGES + '/' + challenge['slug']
    jsonurl = HR_REST + CONTESTS + '/' + challenge['contest_slug'] + CHALLENGES + '/' + challenge['slug']
    html = """<!DOCTYPE html>
    <html><head><meta charset="UTF-8"/>
    <script type="text/javascript" async src="{}">{}</script>
    </head><body><h1>{}</h1><p><a href="{}">Challenge</a> <a href="{}">JSON</a></p><hr/>{}</body></html>
    """.format(asseturl, js, challenge['name'], hrurl, jsonurl, challenge['body_html'])

    filename = challenge['slug'] + '.html'
    with open(filename, 'w') as f:
        f.write(BeautifulSoup(html, "html5lib").prettify() + "\n")
    git.add(filename)

def writeSubmission(sub):
    filename = sub['challenge_slug'] + getFileExtension(sub)
    with open(filename, 'w') as f:
        f.write(sub['code'] + "\n")
    envDict = {'GIT_COMMITTER_DATE': sub['created_at'], 'GIT_AUTHOR_DATE': sub['created_at']}
    msg = "{} ({}) {} {}".format(sub['name'], sub['language'], getFrac(sub['testcase_status']), sub['status'])
    git.add(filename)
    git.commit(m=msg, _ok_code=[0,1], date=sub['created_at'])
    git.commit('--no-edit', amend=True, _env=envDict) # enforce date

def getFileExtension(submission):
    lang = submission['language']
    if lang == 'java' or lang == 'java8':
        return '.java'
    if lang == 'haskell':
        return '.hs'
    if lang == 'prolog' or lang == 'perl':
        return '.pl'
    return '.txt'

def getFrac(testcases):
    return '[{}/{}]'.format(sum(testcases), len(testcases))

