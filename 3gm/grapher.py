import os
import re
import sys
import json
from entities import LegalEntities
from collections import defaultdict
from helpers import connected_components, get_edges
from matplotlib import pyplot as plt
import networkx
from networkx.readwrite import json_graph
from networkx import (
    draw,
    DiGraph,
    Graph,
)


def link_issues(input_dir, outfile):
    graph = defaultdict(set)
    txts = []

    cnt = 0
    ids = {}
    iids = {}

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
                ids[identifier] = cnt
                iids[cnt] = identifier
                cnt += 1


        for entity in LegalEntities.entities:
            neighbors = re.finditer(entity, lines)
            neighbors = [neighbor.group() for neighbor in neighbors]


            for u in neighbors:
                if not u in ids:
                    ids[u] = cnt
                    iids[cnt] = u
                    cnt += 1
                graph[ids[identifier]] |= {ids[u]}
                graph[ids[u]] |= {ids[identifier]}

    components = connected_components(graph)
    print('Number of Connected Components:', len(components))

    avg_degree = 0

    for u in graph.keys():
        avg_degree += len(graph[u])

    avg_degree /= len(graph)

    print('Average Vertex Degree: ', avg_degree)



    G = Graph()

    G.add_edges_from(get_edges(graph))
    for n in G:
        G.nodes[n]['name'] = n

    CC = list(networkx.connected_component_subgraphs(G))
    H = CC[2]

    d = json_graph.node_link_data(H)


    json.dump(d, open(outfile, 'w'), ensure_ascii=False)



if __name__ == '__main__':
    link_issues(sys.argv[1], sys.argv[2])
