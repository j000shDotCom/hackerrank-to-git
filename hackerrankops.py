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
        # TODO remove getCSRF from all hooks
        self.session.hooks['response'].append(addArgsToHook(logAndValidate, getCsrf, session = self.session))
        self.login(username, password)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.logout()

    def login(self, username, password):
        self.session.get(HR + '/dashboard')
        data = {
            'login': username,
            'password': password,
            'remember_me': False,
        }
        self.session.post(HR + '/auth/login', json = data)

    def logout(self):
        return self.session.delete(HR + '/auth/logout')

    def getNewModels(self, models):
        if not models:
            models = {}

        contests = {}
        url = HR_REST + '/hackers/me/myrank_contests'
        contestSlugs = {'master'} | {c['slug'] for c in self.getModels(url)}
        for slug in contestSlugs:
            url = HR_REST + CONTESTS + '/' + slug

            submissionIds = {s['id'] for s in self.getModels(url + SUBMISSIONS)}
            if slug in models and 'submissions' in models[slug]:
                submissionIds -= models[slug]['submissions'].keys()

            if not submissionIds:
                continue

            submissions = contest['submissions'].values()
            challengeSlugs = {sub.json()['model']['challenge_slug'] for sub in submissions}

            contest = {}
            contest['model'] = self.session.get(url).json()['model']
            contest['submissions'] = self.getModelsKeyed(url + SUBMISSIONS, submissionIds)
            contest['challenges'] = self.getModelsKeyed(url + CHALLENGES, challengeSlugs)

            contests[slug] = contest

        return contests

    def getModelsKeyed(self, url, ids):
        models = {}

        for curr, i in enumerate(ids):
            model = self.session.get(url + '/' + str(i), curr = curr, total = len(ids))
            if not model:
                continue
            models[i] = model

        return models

    # get all models from particular GET request
    def getModels(self, url):
        # get initial set of models, usually 4 to 10
        r = self.session.get(url).json()
        models = r['models']
        offset = len(r['models'])
        total = r['total']

        # get the rest of the models (offset, total]
        if offset < total:
            params = {
                'offset': offset,
                'limit': total
            }
            # use params instead of json or data to append to GET query string
            newModels = self.session.get(url, params = params).json()['models']
            models.extend(newModels)

        return models

    def getUserModel(self):
        url = HR_REST + CONTESTS + '/master/hackers/me'
        json = {"updated_modal_profiled_data": {"updated": True}}
        return self.session.put(url, json = json).json()['model']

def addArgsToHook(*factoryArgs, **factoryKwargs):
    def responseHook(response, *requestArgs, **requestKwargs):
        for func in factoryArgs:
            func(response, **factoryKwargs, **requestKwargs)
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
    csrfHtml = BeautifulSoup(r.text, 'html.parser').find(id = 'csrf-token')
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

def logAndValidate(r, *args, **kwargs):
    print(r.status_code, r.request.method, r.request.url, (r.request.body if r.request.body else ''))
    if 'request' in kwargs:
        print('[' + curr + '/' + total + ']')
    if not r.ok:
        raise ValueError('Request Failed: ', r.status_code, r.request.url, r.text)
