"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)
"""
from argparse import ArgumentParser
import hackerrankops as HR
import fileops as IO

def getArgs():
    parser = ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-u', '--username', action='store', metavar='username', required=True, help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', required=True, help='account password')
    parser.add_argument('-f', '--file', action='store', metavar='file', help='create/use pickle file')
    parser.add_argument('-d', '--dir', action='store', metavar='dir', help='path repository path')
    parser.add_argument('-r', '--repo', action='store', metavar='repo', help='remote git repository')
    #parser.add_argument('-b', '--batch', action='store', metavar='batch', type=int, help='challenge request batch size')
    return parser.parse_args();

def main():
    args = getArgs()
    picklePath = IO.getFullPath(args.file)
    archivePath = IO.getFullPath(args.dir)

    models = IO.loadPickle(picklePath)

    (s, csrfHeader) = HR.login(args.username, args.password)
    user = HR.getUserModel(s)
    newModels = HR.getNewModels(s, models)
    HR.logout(s, csrfHeader)

    if not newModels:
        print('no new submissions. exiting.')
        return

    allModels = HR.mergeModels(models, newModels)
    IO.dumpPickle(picklePath, allModels)

    IO.initializeDir(archivePath, user, args.repo)
    sortedModels = HR.sortModels(newModels)
    IO.writeModels(sortedModels)

main()

