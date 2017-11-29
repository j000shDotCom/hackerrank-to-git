"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)
"""

import configparser
from argparse import ArgumentParser
from hackerrankops import HRClient, mergeModels, sortModels
import fileops as IO

import os
import better_exceptions

# TODO store the session id, cookie, token in variables?
def getArgs():
    parser = ArgumentParser(description='Export your code from HackerRank.com!')
    parser.add_argument('-u', '--username', action='store', default=os.environ.get('HR_USER'), help='HR username')
    parser.add_argument('-p', '--password', action='store', default=os.environ.get('HR_PASS'), help='HR password')
    parser.add_argument('-f', '--file', action='store', default=os.environ.get('HR_FILE'), help='load/create file')
    parser.add_argument('-d', '--dir', action='store', default=os.environ.get('HR_REPO'), help='repository path')
    parser.add_argument('--html', action='store_true', help='write contest and challenge html')
    #parser.add_argument('-r', '--repo', action='store', metavar='repo', help='remote git repository')
    return parser.parse_args();

def main():
    args = getArgs()

    # TODO try to create git repository if json file and repo provided
    if not args.username or not args.password:
        print('username or password not provided. exiting.')
        return

    filePath = IO.getFullPath(args.file)
    archivePath = IO.getFullPath(args.dir)
    models = IO.load(filePath)

    user = None
    newModels = None

    # try to login and fetch new models
    # TODO return a partial set of models upon failure
    with HRClient(args.username, args.password) as hrankclient:
        user = hrankclient.getUserModel()
        newModels = hrankclient.getNewModels(models)

    if not newModels:
        print('no new submissions. exiting.')
        return

    # TODO log which submissions are new, different, updated?
    allModels = mergeModels(models, newModels)

    # TODO check if files match?
    if filePath:
        IO.dump(filePath, allModels)

    # TODO do not overwrite files?
    if archivePath:
        IO.initializeDir(archivePath, user, args.dir)
        sortedModels = sortModels(newModels)
        IO.writeModels(sortedModels, args.html)

main()
