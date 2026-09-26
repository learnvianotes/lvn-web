import heapq

class Solution:
    def findCheapestPrice(self, n, flights, src, dst, k):
        graph = [[] for _ in range(n)]

        for u, v, price in flights:
            graph[u].append((v, price))

        # (cost, node, flights taken) - no visited set, so states can repeat
        min_heap = [(0, src, 0)]

        while min_heap:
            cost, node, used = heapq.heappop(min_heap)

            if node == dst:
                return cost

            if used > k:
                continue  # at most k stops = k + 1 flights

            for nxt, price in graph[node]:
                heapq.heappush(min_heap, (cost + price, nxt, used + 1))

        return -1
