class Solution:
    def networkDelayTime(self, times, n, k):
        dist = [float("inf")] * (n + 1)
        dist[k] = 0

        # Relax every edge n - 1 times
        for _ in range(n - 1):
            for u, v, w in times:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w

        answer = max(dist[1:])

        return answer if answer != float("inf") else -1
