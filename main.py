"""
 HackerRank.com scrape
 Joshua Lindsay (jlindsay90@gmail.com)

 Sign into HackerRank and archive solutions in a git repository (where they should be)
"""
from argparse import ArgumentParser
from fileops import archiveData, loadPickle, dumpPickle, updateData
from hackerrankops import getAllData, getLatestData

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
    pickleData = loadPickle(args.file)
    if not pickleData:
        fetchedData = getAllData(args.username, args.password)
        archiveData(args.dir, fetchedData)
        dumpPickle(fetchedData, args.file)
    else:
        newData = getLatestData(args.username, args.password, pickleData)
        archiveData(args.dir, newData)
        data = updateData(pickleData, newData)
        dumpPickle(data, args.file)
main()
