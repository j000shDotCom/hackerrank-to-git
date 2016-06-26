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

def getFullPath(path):
    return os.path.abspath(path)

def loadPickle(filename):
    try:
        models = load(open(filename, 'rb'))
        print('loaded data from pickle')
    except:
        return None
    return models

def dumpPickle(filename, data):
    dump(data, open(filename, 'wb'))
    print('successfully dumped data')

def initializeDir(path, user, repo = None):
    if not os.path.exists(path):
        print('making directories')
        os.makedirs(path)
    os.chdir(path)
    if os.path.exists('.git/'):
        print('git respository already initialized')
        return
    print('initializing git repository')
    git.init()
    os.chmod(path + '/.git/', 0b111000000)
    git.config('--local', 'user.name', '"' + user['name'] + '"')
    git.config('--local', 'user.email', '"' + user['email'] + '"')
    if repo:
        git.remote.add('origin', repo)

def writeModels(models, html):
    if not models:
        return
    print('writing models')
    for t in sorted(models.keys()):
        (m, ty) = models[t]
        if ty == 'co':
            try:
                os.makedirs(m['model']['slug'])
            except:
                pass
            os.chdir(m['model']['slug'])
            if html:
                writeContest(m)
        elif ty == 'ch':
            try:
                os.chdir(m['contest_slug'])
            except:
                os.makedirs(m['contest_slug'])
                os.chdir(m['contest_slug'])
            if html:
                writeChallenge(m)
        elif ty == 'sub':
            os.chdir(m['contest_slug'])
            writeSubmission(m)
        os.chdir('..')

def writeContest(contest):
    model = contest['model']
    hrurl = HR + CONTESTS + '/' + model['slug']
    resturl = HR_REST + CONTESTS + '/' + model['slug']
    challengehtml = '<ul>'
    for (challengeSlug, challenge) in contest['challenges'].items():
        challengehtml += '<li><a href="{}">{}</a></li>'.format(challengeSlug + '.html', challengeSlug)
    challengehtml += '</ul>'
    html = """<!DOCTYPE html>
    <html><head></head><body>
    <h1>{}</h1><a href="{}">Contest</a> <a href="{}">JSON</a><hr/>{}<hr/>
    <h2>Challenges</h2>{}</body></html>
    """.format(model['name'], hrurl, resturl, model['description_html'], challengehtml)

    filename = 'index.html'
    with open(filename, 'w') as f:
        f.write(BeautifulSoup(html, 'html5lib').prettify() + '\n')
    gitCommitModel(contest['model'], filename, 'contest created: ' + model['slug'])

def writeChallenge(challenge):
    asseturl = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML'
    js = "MathJax.Hub.Config({tex2jax:{inlineMath:[['$','$'],['\\(','\\)']]}});"
    hrurl = HR \
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
    gitCommitModel(challenge, filename, 'challenge created: ' + challenge['slug'])

def writeSubmission(sub):
    filename = sub['challenge_slug'] + getFileExtension(sub)
    with open(filename, 'w') as f:
        f.write(sub['code'] + "\n")
    msg = "{} ({}) {} {}".format(sub['name'], sub['language'], getFrac(sub['testcase_status']), sub['status'])
    gitCommitModel(sub, filename, msg)

def gitCommitModel(m, filename, msg):
    envDict = {'GIT_COMMITTER_DATE': m['created_at'], 'GIT_AUTHOR_DATE': m['created_at']}
    git.add(filename)
    git.commit(m=msg, _ok_code=[0,1], date=m['created_at'])
    git.commit('--no-edit', amend=True, _env=envDict) # force date

def getFileExtension(submission):
    lang = submission['language']
    if lang == 'java' or lang == 'java8':
        return '.java'
    if lang == 'python' or lang == 'python3':
        return '.py'
    if lang == 'haskell':
        return '.hs'
    if lang == 'prolog' or lang == 'perl':
        return '.pl'
    return '.txt'

def getFrac(testcases):
    return '[%d/%d]' % (sum(testcases), len(testcases))

