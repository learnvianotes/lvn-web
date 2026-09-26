class Solution:
    def findRedundantConnection(self, edges):
        n = len(edges)
        graph = [[] for _ in range(n + 1)]

        # Is there already a path from u to v?
        def connected(u, v, visited):
            if u == v:
                return True

            visited.add(u)

            for nxt in graph[u]:
                if nxt not in visited and connected(nxt, v, visited):
                    return True

            return False

        for u, v in edges:
            if connected(u, v, set()):
                return [u, v]  # this edge closes a cycle

            graph[u].append(v)
            graph[v].append(u)

        return []
