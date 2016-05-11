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
    if not data['models']:
        return
    createUserPage(data['user'])
    initializeDir(repoPath, data['user']['name'], data['user']['email'])
    models = sortModels(data['models'])
    writeModels(models)

def updateData(data, new):
    models = data['models']
    newModels = new['models']
    for (coSlug, contest) in newModels.items():
        if not coSlug in models:
            models[coSlug] = contest
        for (chSlug, challenge) in contest['challenges'].items():
            if not chSlug in models[coSlug]['challenges']:
                models[coSlug]['challenges'][chSlug] = challenge
        for (sId, submission) in contest['submissions'].items():
            if not sId in models[coSlug]['submissions']:
                models[coSlug]['submissions'] = submission
    data['models'] = models
    return data

def createUserPage(user):
    createdDate = user['created_at']

def initializeDir(path, name, email, repo = None):
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)
    if os.path.exists('.git/'):
        return
    git.init()
    os.chmod(path + '/.git/', 0b111000000)
    git.config('--local', 'user.name', '"' + name + '"')
    git.config('--local', 'user.email', '"' + email + '"')
    if repo:
        git.remote.add('origin', repo)

def sortModels(contests):
    models = dict()
    for co in contests.values():
        models[co['model']['created_at']] = (co, 'co')
        for ch in co['challenges'].values():
            models[ch['created_at']] = (ch, 'ch')
        for s in co['submissions'].values():
            models[s['created_at']] = (s, 'sub')
    return models

def writeModels(models):
    for t in sorted(models.keys()):
        (m, ty) = models[t]
        if ty == 'co':
            try:
                os.makedirs(m['model']['slug'])
            except:
                pass
            os.chdir(m['model']['slug'])
            writeContest(m)
        elif ty == 'ch':
            try:
                os.chdir(m['contest_slug'])
            except:
                os.makedirs(m['contest_slug'])
                os.chdir(m['contest_slug'])
            writeChallenge(m)
        elif ty == 'sub':
            os.chdir(m['contest_slug'])
            writeSubmission(m)
        else:
            print("HOW DID I GET HERE")
            input()
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
    return '[{}/{}]'.format(sum(testcases), len(testcases))

