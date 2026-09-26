from collections import defaultdict

class Solution:
    def findItinerary(self, tickets):
        n = len(tickets)
        tickets = sorted(tickets)

        # airport -> indices of its tickets, in lexical order of destination
        graph = defaultdict(list)

        for i, (src, dst) in enumerate(tickets):
            graph[src].append(i)

        used = [False] * n
        path = ["JFK"]

        def dfs(airport):
            if len(path) == n + 1:
                return True

            for i in graph[airport]:
                if used[i]:
                    continue

                used[i] = True
                path.append(tickets[i][1])

                if dfs(tickets[i][1]):
                    return True

                used[i] = False  # backtrack
                path.pop()

            return False

        dfs("JFK")
        return path
