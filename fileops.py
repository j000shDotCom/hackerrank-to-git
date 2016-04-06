"""
  This file does all the fancy git operations and file writing
"""
import os
from sh import git
from bs4 import BeautifulSoup

def archiveModel(repoPath, model):
    initializeDir(repoPath, model['user']['name'], model['user']['email'])
    for model in model['models']:
        ids = model['ids']
        challenges = model['challenges']
        submissions = model['submissions']
        for c_id in challenges:
            challenge = challenges[c_id]
            subs = [submissions[s_id] for s_id in sorted(ids[c_id])]

            print('inserting ' + challenge['slug'])
            git.checkout(b=challenge['slug'])
            writeChallenge(challenge)
            for sub in subs:
                print('  sub ' + str(sub['id']) + ' ' + sub['status'])
                writeSubmission(sub)

            git.merge(challenge['slug'])
            git.branch(d=challenge['slug'])

def initializeDir(path, name, email):
    if os.path.exists(path):
        os.chdir(path)
        return

    os.makedirs(path)
    os.chdir(path)
    git.init()
    git.config('--local', 'user.name', '"' + name + '"')
    git.config('--local', 'user.email', '"' + email + '"')

    git.checkout(b='master')
    with open('README', 'w') as f:
        f.write('dummy README file to make a commit\n') #TODO
    git.add('README')
    git.commit(m='initial commit')

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

