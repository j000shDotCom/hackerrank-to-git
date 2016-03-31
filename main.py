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
from pickle import load, dump
from requests import Session
from gitops import archiveModel
from hackerrankops import getModelsFromHackerRank

def getArgParser():
    parser = ArgumentParser(description='Free your HackerRank.com code!')
    parser.add_argument('-u', '--username', action='store', metavar='username', help='account username')
    parser.add_argument('-p', '--password', action='store', metavar='password', help='account password')
    parser.add_argument('-f', '--file', action='store', metavar='file', help='create/use pickle file')
    parser.add_argument('-d', '--dir', action='store', metavar='dir', help='path repository path')
    parser.add_argument('-b', '--batch', action='store', metavar='batch', type=int, help='challenge request batch size')
    #parser.add_argument('-l', '--load', action='store_true', metavar='load', help='load pickle file')
    #parser.add_argument('-c', '--create', action='store_true', metavar='create', help='create pickle file')
    return parser;

def main():
    # get args and validate
    parser = getArgParser()
    args = parser.parse_args()
    if not args.username or not args.password:
        parser.print_help()
        exit(123)

    model = None
    if args.file and os.path.exists(args.file):
        model = load(open(args.file, 'rb'))
    else:
        model = getModelsFromHackerRank(Session(), args.username, args.password, args.batch)

    if args.file and not os.path.exists(args.file):
        dump(model, open(args.file, 'wb'))

    archiveModel(args.dir, models)

main()
