import json
import pickle
import io
import re
from os import listdir
from os.path import isfile, join
import networkx as nx
from collections import *
import matplotlib as plt

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
	try: 
		return philObject['query']['pages'].itervalues().next()['revisions'][0]['*']
	except KeyError:
		return None

def findWikiLinks(string):
    pat = r'\[\[([^\|\]]+)\|?([\w\s\D]*?)\]\]'
    matches = re.findall(pat, string)
    return matches

def plotLogDegree(graph):
	d_in = Counter(G.in_degree())
	y_in = Counter(d_in.values()).values()
	x_in = sorted(set(d_in.values()))
	d_out = Counter(G.out_degree())
	y_out = Counter(d_out.values()).values()
	x_out = sorted(set(d_out.values()))
	plt.loglog(x_in,y_in, 'ro-') # Plot the in degree distribution
	plt.loglog(x_out, y_out, 'bv-') # Plot the out degree distribution
	plt.xlabel('Degree')
	plt.ylabel('Number of nodes')
	plt.legend(['In degree', 'Out degree'])
	plt.legend()
	plt.show()

# Load in all the philosophers
phils = [ f for f in listdir('./phils') if isfile(join('./phils',f)) ]

G = nx.DiGraph()

# Create a node for each philosopher
[G.add_node(phil) for phil in phils]

for phil in phils:
	philObject = unpicklePhil(phil)
	philContent = getContent(philObject)
	if philContent:
		links = findWikiLinks(philContent)
		for link in links:
			if link[0] in phils:
				G.add_edge(phil, link[0])

# Find the top 10 linked to philosophers
d_in = Counter(G.in_degree())
d_out = Counter(G.out_degree())
print(d_in(10))
print(d_out(10))


		