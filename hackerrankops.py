"""
 All HackerRank specific logic
"""

import re
from requests import Session
import json
import logging # TODO get rid of these print statements!
from bs4 import BeautifulSoup

HR = 'https://www.hackerrank.com'
HR_REST = HR + '/rest'
CONTESTS = '/contests'
CHALLENGES = '/challenges'
SUBMISSIONS = '/submissions'
SUBMISSIONS_GROUPED = SUBMISSIONS + '/grouped'

class HRClient():
    def __init__(self, username, password):
        self.session = Session()
        self.session.hooks['response'].extend([self.includeSessionInHook(f) for f in [getCsrf, logAndValidate]])
        self.login(username, password)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.logout()

    def login(self, username, password):
        self.session.get(HR + '/dashboard')
        data = {
            'login' : username,
            'password' : password,
            'remember_me' : False,
        }
        self.session.post(HR + '/auth/login', json = data)

    def logout(self):
        return self.session.delete(HR + '/auth/logout')

    def getNewModels(self, models):
        if not models:
            models = {}
        contests = {}
        for slug in self.getContestSlugs():
            print('\n', slug)
            url = HR_REST + CONTESTS + '/' + slug
            submissionIds = self.getSubmissionIds(url)
            if slug in models and 'submissions' in models[slug]:
                submissionIds -= models[slug]['submissions'].keys()
            if not submissionIds:
                continue
            contest = {}
            contest['model'] = self.session.get(url).json()['model']
            contest['submissions'] = self.getModelsKeyed(url + SUBMISSIONS, submissionIds)
            submissions = contest['submissions'].values()
            challengeSlugs = {sub['challenge_slug'] for sub in submissions}
            contest['challenges'] = self.getModelsKeyed(url + CHALLENGES, challengeSlugs)
            contests[slug] = contest
        return contests

    def getContestSlugs(self):
        url = HR_REST + '/hackers/me/myrank_contests?limit=100&type=recent'
        return {'master'} | {c['slug'] for c in self.getModels(url)}

    def getChallengeSlugs(self, url):
        return {c['slug'] for c in self.getModels(url + 'CHALLENGES')}

    def getSubmissionIds(self, url):
        return {s['id'] for s in self.getModels(url + SUBMISSIONS)}

    def getModelsKeyed(self, url, ids):
        print(ids)
        models = {}
        for i in ids:
            model = self.session.get(url + '/' + str(i))
            if not model:
                continue
            models[i] = model
        return models

    def getModels(self, url):
        r = self.session.get(url).json()
        return r['models'] + self.getModelRange(url, len(r['models']), r['total'])

    def getModelRange(self, url, start, end):
        if start >= end:
            return []
        offset = {'params': {'offset': start, 'limit': end}}
        return self.session.get(url, offset).json()['models']

    def getUserModel(self):
        return self.session.put(HR_REST + CONTESTS + '/master/hackers/me', json = {"updated_modal_profiled_data":{"updated":True}})


    def includeSessionInHook(self, *factory_args, **factory_kwargs):
        def responseHook(response, *request_args, **request_kwargs):
            
            for func in factory_args:
                func(response, session = self.session)

            return response
        return responseHook

def mergeModels(models, newModels):
    if not newModels:
        return models or {}
    if not models:
        return newModels or {}
    for slug in newModels.keys():
        if slug not in models:
            models[slug] = newModels[slug]
            continue
        old = models[slug]
        new = newModels[slug]
        old['model'] = new['model']
        old['challenges'].update(new['challenges'])
        old['submissions'].update(new['submissions'])
    return models

def sortModels(contests):
    models = dict()
    for co in contests.values():
        models[co['model']['created_at']] = (co, 'co')
        for ch in co['challenges'].values():
            models[ch['created_at']] = (ch, 'ch')
        for s in co['submissions'].values():
            models[s['created_at']] = (s, 'sub')
    return models

def getCsrf(r, *args, **kwargs):
    soup = BeautifulSoup(r.text, 'html5lib')
    csrfHtml = soup.find(id='csrf-token')
    if csrfHtml:
        csrfHtml = csrfHtml['content']

    j = None
    csrfJson = None
    try:
        j = json.loads(r.content)
        if 'csrf_token' in j:
            csrfJson = j['csrf_token']
        elif '_csrf_token' in j:
            csrfJson = j['_csrf_token']
    except Exception:
        pass
    
    csrf = csrfHtml or csrfJson
    if 'session' in kwargs and csrf:
        kwargs['session'].headers.update({'X-CSRF-TOKEN': csrf})
        print('CSRF', csrf)

def logAndValidate(r, *args, **kwargs):
    print('-' * 50)
    print(r.status_code, r.request.method, r.request.url)
    if r.cookies:
        for cookie in r.cookies:
            print(cookie)
    if r.history:
        print('REDIRECT', r.history)
    if not r.ok:
        raise ValueError('Request Failed: ', r.status_code, r.request.url, r.text)
    #if '_hrank_session' not in r.cookies.keys():
    #    raise ValueError('The _hrank_session is not there!', r.cookies.keys())

def printText(r, *args, **kwargs):
    print(r.text)