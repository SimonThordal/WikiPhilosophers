from __future__ import print_function
import json
import pickle
import urllib2 as url
import re
import io
import sys

def safeprint(s):
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            print(s.encode('utf8').decode(sys.stdout.encoding))
        else:
            print(s.encode('utf8'))

endpoint = 'https://da.wikipedia.org/w/api.php'
action = 'query'
prop = 'revisions'
rvprop = 'content'
title = 'Hans_Hermannsen'
data = "action={}&titles={}&prop={}&rvprop={}&format=json&continue=".format(action,title,prop, rvprop)
u = url.urlopen(endpoint, data)
data = json.loads(u.readlines()[0])

with io.open('spam.txt', 'wb') as file:
	pickle.dump(data, file, protocol=2)

with io.open('spam.txt', 'rb') as file:
	unpickled = pickle.load(file)

text=unpickled['query']['pages'].itervalues().next()['revisions'][0]['*']

# Find tricky link (with ø) and find it on the api
pat = r'\[\[([^\|\]]+)\|?([\w\s\D]*?)\]\]'
matches = re.findall(pat, text)
title = url.quote(matches[5][0].encode('utf-8'))
data = "action={}&titles={}&prop={}&rvprop={}&format=json&continue=".format(action,title,prop, rvprop)
u = url.urlopen(endpoint, data)
data = json.loads(u.readlines()[0])
print(data)