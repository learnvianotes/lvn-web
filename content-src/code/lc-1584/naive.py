class Solution:
    def minCostConnectPoints(self, points):
        n = len(points)

        # Build every edge (dist, i, j) and sort them
        edges = []

        for i in range(n):
            for j in range(i + 1, n):
                dist = (
                    abs(points[i][0] - points[j][0])
                    + abs(points[i][1] - points[j][1])
                )
                edges.append((dist, i, j))

        edges.sort()

        parent = list(range(n))

        def find(x):
            while x != parent[x]:
                parent[x] = parent[parent[x]]
                x = parent[x]

            return x

        total_cost = 0
        used = 0

        for dist, i, j in edges:
            root_i = find(i)
            root_j = find(j)

            if root_i == root_j:
                continue

            parent[root_i] = root_j
            total_cost += dist
            used += 1

            if used == n - 1:
                break

        return total_cost
