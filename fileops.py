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
            challenge = contest['challenges'][submission['challenge_slug']]
            writeChallenge(challenge)
            writeSubmission(submission)

        os.chdir('..')

def initializeDir(path, name, email):
    os.makedirs(path)
    os.chdir(path)
    git.init()
    git.config('--local', 'user.name', '"' + name + '"')
    git.config('--local', 'user.email', '"' + email + '"')

def writeContest(contest):
    html = '<!DOCTYPE html><html><head></head><body>' \
        + contest['description_html'] \
        + '</body></html>'
    filename = contest['slug'] + '.html'
    with open(filename, 'w') as f:
        f.write(BeautifulSoup(html, 'html.parser').prettify() + '\n')
    git.add(filename)

def writeChallenge(challenge):
    html = '<!DOCTYPE html><html><head><script type="text/javascript" async ' \
        + 'src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML">'\
        + "MathJax.Hub.Config({tex2jax:{inlineMath:[['$','$'],['\\(','\\)']]}});"\
        + '</script></head><body>' + challenge['body_html'] + '</body></html>'
    filename = challenge['slug'] + '.html'
    with open(filename, 'w') as f:
        f.write(BeautifulSoup(html, 'html.parser').prettify() + "\n")
    git.add(filename)

def writeSubmission(sub):
    filename = sub['challenge_slug'] + getFileExtension(sub)
    msg = "{} ({}) {} {}".format(sub['name'], sub['language'], getFrac(sub['testcase_status']), sub['status'])
    envDict = {'GIT_COMMITTER_DATE':sub['created_at'], 'GIT_AUTHOR_DATE':sub['created_at']}
    with open(filename, 'w') as f:
        f.write(sub['code'] + "\n")
    git.add(filename)
    git.commit(m=msg, _ok_code=[0,1], date=sub['created_at'], _env=envDict)
    git.commit('--no-edit', amend=True, _env=envDict)

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

