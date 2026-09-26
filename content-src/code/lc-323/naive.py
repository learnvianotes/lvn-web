class Solution:
    def countComponents(self, n, edges):
        graph = [[] for _ in range(n)]

        for a, b in edges:
            graph[a].append(b)
            graph[b].append(a)

        visited = [False] * n

        def dfs(node):
            visited[node] = True

            for neighbor in graph[node]:
                if not visited[neighbor]:
                    dfs(neighbor)

        components = 0

        for node in range(n):
            if not visited[node]:
                components += 1
                dfs(node)

        return components
