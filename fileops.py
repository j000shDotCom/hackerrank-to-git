"""
  This file does all the fancy git operations and file writing
"""
import os
from pickle import load, dump
from bs4 import BeautifulSoup
from sh import git

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
    initializeDir(repoPath, data['user']['name'], data['user']['email'])
    for (contestSlug, contest) in data['models'].items():
        git.checkout(b=contestSlug)
        os.makedirs(contestSlug)
        os.chdir(contestSlug)
        writeContest(contest)
        #gitCommitModel(contest)

        for (challengeSlug, challenge) in contest['challenges'].items():
            writeChallenge(challenge)
        for (submissionId, submission) in sorted(contest['submissions'].items()):
            writeSubmission(submission)

        os.chdir('..')

    git.checkout('master')
    for contestSlug in data['models'].keys():
        git.merge(contestSlug)

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
    hrurl = 'https://www.hackerrank.com/contests/' + contest['slug']
    resturl = 'https://www.hackerrank.com/rest/contests/' + contest['slug']
    challengehtml = '<ul>'
    for (challengeSlug, challenge) in contest['challenges'].items():
        challengehtml += '<li><a href="{}">{}</a></li>'.format(challengeSlug + '.html', challengeSlug)
    challengehtml += '</ul>'
    html = """<!DOCTYPE html>
    <html><head></head><body>
    <h1>{}</h1><a href="{}">Contest</a> <a href="{}">JSON</a><hr/>{}<hr/>
    <h2>Challenges</h2>{}</body></html>
    """.format(contest['name'], hrurl, resturl, contest['description_html'], challengehtml)

    with open('index.html', 'w') as f:
        f.write(BeautifulSoup(html, 'html5lib').prettify() + '\n')
    git.add('index.html')

def writeChallenge(challenge):
    asseturl = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML'
    js = "MathJax.Hub.Config({tex2jax:{inlineMath:[['$','$'],['\\(','\\)']]}});"
    hrurl = 'https://www.hackerrank.com' \
        + ('/contests/' + challenge['contest_slug'] if challenge['contest_slug'] != 'master' else '') \
        + '/challenges/' + challenge['slug']
    jsonurl = 'https://www.hackerrank.com/rest/contests/' + challenge['contest_slug'] \
        + '/challenges/' + challenge['slug']
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
    envDict = {'GIT_COMMITTER_DATE':sub['created_at'], 'GIT_AUTHOR_DATE':sub['created_at']}
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

