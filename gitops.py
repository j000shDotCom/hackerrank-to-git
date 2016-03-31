"""
  This file does all the fancy git operations and file writing
"""
import os
from sh import git

def archiveModel(repoPath, model):
    initializeDir(repoPath)
    ids = model['ids']
    challenges = model['challenges']
    submissions = model['submissions']
    for c_id in challenges:
        challenge = challenges[c_id]
        subs = [submissions[s_id] for s_id in ids[c_id]]

        git.checkout(b=challenge['slug'])
        writeChallenge(challenge)
        writeSubmissions(subs)

        git.checkout('master')
        git.merge(challenge['slug'])
        git.branch(d=challenge['slug'])

def initializeDir(path):
    if os.path.exists(path):
        os.chdir(path)
        return
    os.makedirs(path)
    os.chdir(path)
    git.init()
    with open('README', 'w') as f:
        f.write('dummy README file to make a commit\n') #TODO
    git.add('README')
    git.commit(m='initial commit')

def writeChallenge(challenge):
    filename = challenge['slug'] + '.html'
    print('generating ' + filename)
    with open(filename, 'w') as f:
        f.write('<!DOCTYPE html><html><head><script type="text/javascript" async '\
            + 'src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML">'\
            + "MathJax.Hub.Config({tex2jax:{inlineMath:[['$','$'], ['\\(','\\)']]}});"\
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

def getFrac(testcases):
    return '[{}/{}]'.format(sum(testcases), len(testcases))

