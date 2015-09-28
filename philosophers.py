from __future__ import print_function
import json
import pickle
import urllib2 as url
import re
import sys

def safeprint(s):
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            print(s.encode('utf8').decode(sys.stdout.encoding))
        else:
            print(s.encode('utf8'))

# Call this on JSON data to make sure it's utf-8
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

# First get the lists of different philophers
branches = ["List_of_aestheticians","List_of_epistemologists","List_of_ethicists","List_of_logicians","List_of_metaphysicians","List_of_social_and_political_philosophers"]
endpoint = 'https://en.wikipedia.org/w/api.php'
action = 'query'
pllimit = 500
prop = 'links'
branchData = []
for branch in branches:
    title = branch
    data = "action={}&titles={}&prop={}&pllimit={}&format=json&continue=".format(action,title,prop, pllimit)
    u = url.urlopen(endpoint, data)
    data = json.loads(u.readlines()[0])
    branchData.append(data)

# Remove any titles that have words with non-capital letters that are not 'of', 'von' or 'de'
for phil in branchData:
    links = phil['query']['pages'].itervalues().next()['links']
    for link in links:
        matches = [re.search(r'(?!^of$)(?!^von$)(?!^de$)^[a-z]+', word) for word in link['title'].split(" ")]
        if any(matches):
            links.remove(link)

# Find number of branchData in different branches
p = []
for i in range(0, len(branchData)):
    key = branchData[i]['query']['pages'].itervalues().next()['title']
    p.append((key, []))
    for link in branchData[i]['query']['pages'].itervalues().next()['links']:
        p[i][1].append(link['title'])
for branch in p:
    safeprint("Length of {}:{}".format(branch[0].lower(), len(branch[1])))

# Find the overlap between different branches
overlap = []
for i in range(0, len(p)):
    for j in range(0, len(p)):
        if (i==j):
            continue
        s1 = set(p[i][1]);
        s2 = set(p[j][1]);
        t = "{} and the {}".format(p[i][0], p[j][0])
        overlap.append((t, s1.intersection(s2)))
for intersection in overlap:
    safeprint("Overlap between the {}:".format(intersection[0].lower()))
    for name in intersection[1]:
        safeprint(name)
    print()

# Find the most prominent philosopher
from collections import Counter
c = Counter()
for tup in p:
    l = tup[1]
    c.update(l)