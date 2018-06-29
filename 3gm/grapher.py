import os
import re
import sys
from entities import LegalEntities
from collections import defaultdict
from helpers import connected_components, get_edges
from matplotlib import pyplot as plt
import networkx
from networkx import (
    draw,
    DiGraph,
    Graph,
)

graph = defaultdict(set)

txts = []
input_dir = sys.argv[1]

for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith('.txt'):
            txts.append(os.path.join(root, file))

for infile in txts:
    with open(infile) as f:
        lines = f.read().splitlines()
    year = infile.split('/')[-2]
    lines = ' '.join(lines)
    lines = re.sub(' +', ' ', lines)

    for ratification in LegalEntities.ratifications:
        result = re.search(ratification, lines)
        if result:
            result = result.group().rstrip().split(' ')

            abbreviation = 'ν.'

            if result[0] == 'ΠΡΟΕΔΡΙΚΟ':
                abbreviation = 'π.δ.'
            elif result[0] == 'ΚΟΙΝΗ':
                abbreviation = 'ΚΥΑ'
            elif result[0] == 'ΝΟΜΟΘΕΤΙΚΟ':
                abbreviation = 'ν.δ.'

            identifier = '{} {}/{}'.format(abbreviation, result[-1], year)
            print('Identifier')
            print(identifier)

    for entity in LegalEntities.entities:
        neighbors = re.finditer(entity, lines)
        neighbors = [neighbor.group() for neighbor in neighbors]

        for u in neighbors:
            graph[identifier] |= {u}
            graph[u] |= {identifier}

components = connected_components(graph)
print('Number of Connected Components:', len(components))

avg_degree = 0

for u in graph.keys():
    avg_degree += len(graph[u])

avg_degree /= len(graph)

print('Average Vertex Degree: ', avg_degree)

G = Graph()
G.add_edges_from(get_edges(graph))
draw(G, with_labels=True, edge_color='g', width=0.1, node_color='g')
plt.show()
