"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)
"""
import configparser
from argparse import ArgumentParser
from hackerrankops import HRClient
import fileops as IO

#import better_exceptions

def getArgs():
    parser = ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-u', '--username', action='store', required=True, help='account username')
    parser.add_argument('-p', '--password', action='store', required=True, help='account password')
    parser.add_argument('-f', '--file', action='store', required=True, help='create/use pickle file')
    parser.add_argument('-d', '--dir', action='store', help='path repository path')
    parser.add_argument('--html', action='store_true', help='write contest and challenge html')
    #parser.add_argument('-r', '--repo', action='store', metavar='repo', help='remote git repository')
    #parser.add_argument('-b', '--batch', action='store', metavar='batch', type=int, help='challenge request batch size')
    return parser.parse_args();

def main():
    args = getArgs()
    picklePath = IO.getFullPath(args.file)
    archivePath = IO.getFullPath(args.dir)
    models = IO.loadPickle(picklePath)

    with HRClient(args.username, args.password) as hrankclient:
        user = hrankclient.getUserModel()
        newModels = hrankclient.getNewModels(models)

    return
    if not newModels:
        print('no new submissions. exiting.')
        return

    allModels = HR.mergeModels(models, newModels)
    IO.dumpPickle(picklePath, allModels)

    IO.initializeDir(archivePath, user, args.dir)
    sortedModels = HR.sortModels(newModels)
    IO.writeModels(sortedModels, args.html)

main()

