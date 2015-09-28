from __future__ import print_function
import json
import pickle
import urllib2 as url
import re
import sys
import io
from os import listdir
from os.path import isfile, join
from philHelpers import *

def safeprint(s):
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            print(s.encode('utf8').decode(sys.stdout.encoding))
        else:
            print(s.encode('utf8'))

def unpicklePhil(name):
    path = 'phils/' + name
    with io.open(path, 'rb') as file:
        d = pickle.load(file)
    picklePhil(name, d)
    return d

def picklePhil(name, data):
    path = 'phils/' + name
    with io.open(path, 'wb') as file:
        pickle.dump(data, file, protocol=2)

def getContent(philObject):
    return philObject['query']['pages'].itervalues().next()['revisions'][0]['*']

def findWikiLinks(string):
    pat = r'\[\[([^\|\]]+)\|?([\w\s\D]*?)\]\]'
    matches = re.findall(pat, string)
    return matches

# First get the lists of different philophers
branches = ["List_of_aestheticians","List_of_epistemologists","List_of_ethicists","List_of_logicians","List_of_metaphysicians","List_of_social_and_political_philosophers"]
endpoint = 'https://en.wikipedia.org/w/api.php'
action = 'query'
pllimit = 500
prop = 'links'
branchData = []

# Download the list of philosophers if we did not already save them
if not isfile('phillist.txt'):
    for branch in branches:
        title = branch
        data = "action={}&titles={}&prop={}&pllimit={}&format=json&continue=".format(action,title,prop, pllimit)
        u = url.urlopen(endpoint, data)
        data = json.loads(u.readlines()[0])
        branchData.append(data)
    with io.open('phillist.txt', 'wb') as file:
        pickle.dump(branchData, file, protocol=2)
else:
    with io.open('phillist.txt', 'rb') as file:
        branchData = pickle.load(file)

# Remove any titles that have words with non-capital letters that are not 'of', 'von' or 'de' and store the philo
# -sophers in a list of tuples instead
p = []
regFilter = r'(?!^of$)(?!^von$)(?!^de$)^[a-z]+|Wiki|[\:\\\/]'
for i in range(0, len(branchData)):
    key = branchData[i]['query']['pages'].itervalues().next()['title']
    p.append((key, []))
    links = branchData[i]['query']['pages'].itervalues().next()['links']
    for link in links:
        matches = [re.search(regFilter, word) for word in link['title'].split(" ")]
        if not any(matches):
            p[i][1].append(link['title'])

# Find number of branchData in different branches
for branch in p:
    safeprint("Length of {}:{}".format(branch[0].lower(), len(branch[1])))

philSet = set()
for i in range(0, len(p)):
    s = set(p[i][1])
    philSet = philSet.union(s)

# Find the ones we've already downloaded
onlyfiles = [ f for f in listdir('./phils') if isfile(join('./phils',f)) ]
# Fetch each philosopher
uniquePhils = list(philSet.difference(set(onlyfiles)))
prop = 'revisions'
rvprop = 'content'
for i in range(0, len(uniquePhils)):
    title = url.quote(uniquePhils[i].encode('utf-8'))
    safeprint("Fetching" + title)
    data = "action={}&titles={}&prop={}&rvprop={}&format=json&continue=".format(action,title,prop, rvprop)
    u = url.urlopen(endpoint, data)
    wikiData = json.loads(u.readlines()[0])
    picklePhil(uniquePhils[i], wikiData)