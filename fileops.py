"""
  This file does all the fancy git operations and file writing
"""
import os
from pickle import load, dump
from bs4 import BeautifulSoup
from sh import git

def loadPickle(filename):
    return load(open(filename, 'rb'))

def dumpPickle(data, filename):
    dump(data, open(filename, 'wb'))

def archiveData(repoPath, data):
    initializeDir(repoPath, data['user']['name'], data['user']['email'])
    for (contestSlug, contest) in data['models'].items():
        os.makedirs(contestSlug)
        os.chdir(contestSlug)
        writeContest(contest['model'])
        for (submissionId, submission) in sorted(contest['submissions'].items()):
            # TODO add each contest to its own branch since submissions are sorted at contest level
            challenge = contest['challenges'][submission['challenge_slug']]
            writeChallenge(challenge)
            writeSubmission(submission)
        os.chdir('..')

def initializeDir(path, name, email):
    os.makedirs(path)
    os.chdir(path)
    git.init()
    os.chmod(path + '/.git/', 0b111000000)
    git.config('--local', 'user.name', '"' + name + '"')
    git.config('--local', 'user.email', '"' + email + '"')

def writeContest(contest):
    #TODO url generator class/function/lambda
    hrurl = 'https://www.hackerrank.com/contests/' + contest['slug']
    resturl = 'https://www.hackerrank.com/rest/contests/' + contest['slug']
    html = '<!DOCTYPE html><html><head>'\
        + '</head><body>' \
        + '<h1>' + contest['name'] + '</h1>' \
        + '<a href="' + hrurl +'" target="_blank">Contest</a> ' \
        + '<a href="' + resturl + '" target="_blank">JSON</a> ' \
        + '<hr/>' \
        + contest['description_html'] \
        + '</body></html>'
    # TODO include links to challenges and REST endpoints
    filename = contest['slug'] + '.html'
    with open(filename, 'w') as f:
        f.write(BeautifulSoup(html, 'html.parser').prettify() + '\n')
    msg = 'begin contest ' + contest['name']
    gitCommitModel(filename, contest, msg)

def writeChallenge(challenge):
    hrurl = 'https://www.hackerrank.com' \
        + ('/contests/' + challenge['contest_slug'] if challenge['contest_slug'] != 'master' else '') \
        + '/challenges/' + challenge['slug']
    jsonurl = 'https://www.hackerrank.com/rest/contests/' + challenge['contest_slug'] \
        + '/challenges/' + challenge['slug']
    html = '<!DOCTYPE html><html><head>'\
        + '<meta charset="UTF-8"/>'\
        + '<script type="text/javascript" async ' \
        + 'src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML">'\
        + "MathJax.Hub.Config({tex2jax:{inlineMath:[['$','$'],['\\(','\\)']]}});</script>\n"\
        + '</head><body>'\
        + '<h1>' + challenge['name'] + '</h1>' \
        + '<a href="' + hrurl + '" target="_blank">Challenge</a> ' \
        + '<a href="' + jsonurl + '" target="_blank">JSON</a> ' \
        + '<hr/>' \
        + challenge['body_html'] \
        + '</body></html>'
    filename = challenge['slug'] + '.html'
    with open(filename, 'w') as f:
        f.write(BeautifulSoup(html, 'html.parser').prettify() + "\n")
    msg = 'begin challenge ' + challenge['name']
    gitCommitModel(filename, challenge, msg)

def writeSubmission(sub):
    filename = sub['challenge_slug'] + getFileExtension(sub)
    with open(filename, 'w') as f:
        f.write(sub['code'] + "\n")
    msg = "{} ({}) {} {}".format(sub['name'], sub['language'], getFrac(sub['testcase_status']), sub['status'])
    gitCommitModel(filename, sub, msg)

def gitCommitModel(filename, model, message):
    envDict = {'GIT_COMMITTER_DATE':model['created_at'], 'GIT_AUTHOR_DATE':model['created_at']}
    git.add(filename)
    git.commit(m=message, _ok_code=[0,1], date=model['created_at'])
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

