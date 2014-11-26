import pqdict

def dijkstra(graph, source, target=None):
    """
    Computes the shortests paths from a source vertex to every other vertex in
    a graph

    """
    # The entire main loop is O( (m+n) log n ), where n is the number of
    # vertices and m is the number of edges. If the graph is connected
    # (i.e. the graph is in one piece), m normally dominates over n, making the
    # algorithm O(m log n) overall.

    dist = {}   
    pred = {}

    # Store distance scores in a priority queue dictionary
    pq = pqdict.PQDict()
    for node in graph:
        if node == source:
            pq[node] = 0
        else:
            pq[node] = float('inf')

    # Remove the head node of the "frontier" edge from pqdict: O(log n).
    for node, min_dist in pq.iteritems():
        # Each node in the graph gets processed just once.
        # Overall this is O(n log n).
        dist[node] = min_dist
        if node == target:
            break

        # Updating the score of any edge's node is O(log n) using pqdict.
        # There is _at most_ one score update for each _edge_ in the graph.
        # Overall this is O(m log n).
        for neighbor in graph[node]:
            if neighbor in pq:
                new_score = dist[node] + graph[node][neighbor]
                if new_score < pq[neighbor]:
                    pq[neighbor] = new_score
                    pred[neighbor] = node

    return dist, pred

def shortest_path(graph, source, target):
    dist, pred = dijkstra(graph, source, target)
    end = target
    path = [end]
    while end != source:
        end = pred[end]
        path.append(end)        
    path.reverse()
    return path

if __name__=='__main__':
    # A simple edge-labeled graph using a dict of dicts
    graph = {'a': {'b':1, 'c':9999},
             'b': {'a':9999, 'c':1},
             'c': {'a':1, 'b':1}}

    print "shortest_path(g, a, b) = ", 
    print shortest_path(graph, 'a', 'b')
    
    print "shortest_path(g, a, c) = ", 
    print shortest_path(graph, 'a', 'c')
    
    print "shortest_path(g, b, a) = ", 
    print shortest_path(graph, 'b', 'a')
    
    print "shortest_path(g, b, c) = ", 
    print shortest_path(graph, 'b', 'c')
    
    print "shortest_path(g, c, a) = ", 
    print shortest_path(graph, 'c', 'a')
    
    print "shortest_path(g, c, b) = ", 
    print shortest_path(graph, 'c', 'b')    
    
    
