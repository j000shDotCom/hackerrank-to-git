"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)
"""
from argparse import ArgumentParser
from fileops import archiveData, loadPickle, dumpPickle
from hackerrankops import getHackerRankData

def getArgs():
    parser = ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-u', '--username', action='store', metavar='username', required=True, help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', required=True, help='account password')
    parser.add_argument('-f', '--file', action='store', metavar='file', help='create/use pickle file')
    parser.add_argument('-d', '--dir', action='store', metavar='dir', help='path repository path')
    #parser.add_argument('-b', '--batch', action='store', metavar='batch', type=int, help='challenge request batch size')
    return parser.parse_args();

def main():
    args = getArgs()
    data = loadPickle(args.file)
    if not data:
        data = getHackerRankData(args.username, args.password)
        dumpPickle(data, args.file)
    archiveData(args.dir, data)

main()
