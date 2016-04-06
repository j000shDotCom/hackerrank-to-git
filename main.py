"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)

 Relevant Links:
 https://www.hackerrank.com/rest/contests/master/submissions/grouped?offset=0limit=2
 https://www.hackerrank.com/rest/hackers/{username}/recent_challenges?offset=0&limit=2
 https://www.hackerrank.com/rest/contests/master/challenges?limit=132352
 https://www.hackerrank.com/rest/contests/master/challenges/{slug or challengeId}
 https://www.hackerrank.com/rest/contests/master/submissions/{submissionId}
 https://www.hackerrank.com/rest/contests/master/challenges/{slug}/submissions/?offset=0&limit=10
"""
import os.path
from argparse import ArgumentParser
from requests import Session
from gitops import archiveData
from hackerrankops import getHackerRankData

def getArgs():
    parser = ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-u', '--username', action='store', metavar='username', required=True, help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', required=True, help='account password')
    parser.add_argument('-f', '--file', action='store', metavar='file', help='create/use pickle file')
    parser.add_argument('-d', '--dir', action='store', metavar='dir', help='path repository path')
    parser.add_argument('-b', '--batch', action='store', metavar='batch', type=int, help='challenge request batch size')
    #parser.add_argument('-l', '--load', action='store_true', metavar='load', help='load pickle file')
    #parser.add_argument('-c', '--create', action='store_true', metavar='create', help='create pickle file')
    return parser.parse_args();

def main():
    args = getArgs()

    #if args.file and os.path.exists(args.file):
    #    model = load(open(args.file, 'rb'))
    #else:

    s = Session()
    data = getHackerRankData(s, args.username, args.password, args.batch)

    # cannot pickle generator TODO
    #if args.file and not os.path.exists(args.file):
    #    dump(models, open(args.file, 'wb'))

    archiveData(args.dir, data)

main()
