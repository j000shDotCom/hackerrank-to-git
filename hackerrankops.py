"""
 All HackerRank specific logic
"""

import re
from requests import Session
from requests.auth import AuthBase, HTTPBasicAuth
import json
import logging # TODO get rid of these print statements!
from bs4 import BeautifulSoup

HR = 'https://www.hackerrank.com'
HR_REST = HR + '/rest'
CONTESTS = '/contests'
CHALLENGES = '/challenges'
SUBMISSIONS = '/submissions'
SUBMISSIONS_GROUPED = SUBMISSIONS + '/grouped'

# TODO use the request auth parameter
class HRAuth(AuthBase):
    def __init__(self, username, password, csrf):
        self.username = username
        self.password = password
        self.csrf = csrf

    def __call__(self, r):
        r.headers['X-CSRF-TOKEN'] = self.csrf
        return r

class HRClient():
    def __init__(self, username, password):
        self.session = Session()
        self.session.hooks['response'].append(addArgsToHook(logAndValidate, getCsrf, session = self.session))
        self.login(username, password)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.logout()

    # added dummy timeout argument to not skip CSRF passing
    def login(self, username, password):
        self.session.get(HR + '/dashboard', timeout = 120)
        data = {
            'login': username,
            'password': password,
            'remember_me': False,
        }
        self.session.post(HR + '/auth/login', json = data, timeout = 120)

    # added dummy timeout argument to not skip CSRF passing
    def logout(self):
        return self.session.delete(HR + '/auth/logout', timeout = 120)

    # added dummy timeout argument to not skip CSRF passing
    def getUserModel(self):
        url = HR_REST + CONTESTS + '/master/hackers/me'
        json = {"updated_modal_profiled_data": {"updated": True}}
        hooks = {'response': addArgsToHook(logAndValidate, getCsrf, session = self.session)}
        return self.session.put(url, json = json, hooks = hooks).json()['model']

    def getNewModels(self, models):
        if not models:
            models = {}

        contests = {}
        url = HR_REST + '/hackers/me/myrank_contests'
        contestSlugs = {'master'} | {c['slug'] for c in self.getModels(url, type = 'recent')}
        for slug in contestSlugs:
            url = HR_REST + CONTESTS + '/' + slug

            submissionIds = {s['id'] for s in self.getModels(url + SUBMISSIONS)}
            if slug in models and 'submissions' in models[slug]:
                submissionIds -= models[slug]['submissions'].keys()

            if not submissionIds:
                continue

            contestModel = self.session.get(url).json()['model']
            submissions = self.getModelsKeyed(url + SUBMISSIONS, submissionIds)
            challengeSlugs = {sub['challenge_slug'] for sub in submissions.values()}

            contest = {}
            contest['model'] = contestModel
            contest['submissions'] = submissions
            contest['challenges'] = self.getModelsKeyed(url + CHALLENGES, challengeSlugs)

            contests[slug] = contest

        return contests

    def getModelsKeyed(self, url, ids):
        models = {}
        count = len(ids)

        for curr, i in enumerate(ids):
            model = self.session.get(url + '/' + str(i), data = {'curr': curr + 1, 'total': count, 'rem': total - curr - 1}).json()['model']
            if not model:
                continue
            models[i] = model

        return models

    # get all models from particular GET request
    def getModels(self, url, **params):
        # get initial set of models, usually 4 to 10
        r = self.session.get(url, params = params).json()
        models = r['models']
        offset = len(r['models'])
        total = r['total']

        # get the rest of the models (offset, total]
        if offset < total:
            params['offset'] = offset
            params['limit'] = total
            r = self.session.get(url, params = params).json()
            models.extend(r['models'])

        return models

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
    if not kwargs['timeout']:
        return

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
    parts = [r.status_code, r.request.method, r.request.url]
    if r.request.body:
        parts.append(r.request.body)
    print(*parts)

    if not r.ok:
        raise ValueError('Request Failed: ', r.status_code, r.request.url, r.text)
