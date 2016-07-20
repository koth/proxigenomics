#!/usr/bin/env python
import numpy as np
import networkx as nx
import argparse
import sys
import os



def pick_node(node_map, rs):
    try:
        pos = rs.randint(0, node_map['ranges'][-1])
        idx = np.argwhere(node_map['ranges'] < pos)[-1][0]
        return node_map['ids'][idx]
    except IndexError as er:
        print er
        print pos, idx
        print node_map
        sys.exit(1)


def noise_edges_prop(g, noise_rate, seed):
    rs = np.random.RandomState(seed)

    # calculate total weight of edges, for a raw weighted graph
    # this is the total number of observed edges.
    total_weight = 0
    for u, v, d in g.edges_iter(data=True):
        total_weight += d['weight']
    print 'Total graph weight {0}'.format(total_weight)

    # the number of noise edges is set relative to the total edge weight
    n_edges = int(total_weight * noise_rate)
    print 'Specified rate {0:.3e} will generate {1} spurious observations'.format(noise_rate, n_edges)

    node_map = {'ids': [None], 'ranges': [0]}
    max_pos = 0
    for u, d in g.nodes_iter(data=True):
        max_pos += d['length']
        node_map['ranges'].append(max_pos)
        node_map['ids'].append(u)

    node_map['ids'][0] = node_map['ids'][1]
    node_map['ranges'] = np.array(node_map['ranges'])
    node_map['ids'] = np.array(node_map['ids'])

    g_out = g.copy()
    for n in xrange(n_edges):
        u = pick_node(node_map, rs)
        while True:
            v = pick_node(node_map, rs)
            if v != u: break
        if g_out.has_edge(u, v):
            g_out[u][v]['weight'] += 1
        else:
            g_out.add_edge(u, v, weight=1)

    print 'Initial graph |n|={0} |e|={1}'.format(g.order(), g.size())
    print 'Noisy graph |n|={0} |e|={1}'.format(g_out.order(), g_out.size())

    return g_out

parser = argparse.ArgumentParser(description='Add random edges to a graph')
parser.add_argument('-s', '--seed', required=True, type=int, help='Primary seed')
parser.add_argument('-p', '--error-rate', required=True, type=float,
                    help='Rate of error edges relative to total edge weight')
parser.add_argument('-n', '--replicates', type=int, default=1, help='Number of replicate graphs to generate')
parser.add_argument('graph', metavar='GRAPHML', help='Graph to inject noise')

args = parser.parse_args()

seed_list = np.random.RandomState(args.seed).randint(1000000, 5000000, args.replicates)

g = nx.read_graphml(args.graph)

base_name = os.path.splitext(os.path.basename(args.graph))[0]

for n, seed in enumerate(seed_list, start=1):
    print 'Graph {0}, using random seed {1}'.format(n, seed)
    g_out = noise_edges_prop(g, args.error_rate, seed)
    nx.write_graphml(g_out, '{0}_nsy{1}.graphml'.format(base_name, n))
    print ''




