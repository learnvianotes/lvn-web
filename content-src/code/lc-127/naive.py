from collections import deque

class Solution:
    def ladderLength(self, beginWord, endWord, wordList):
        if endWord not in wordList:
            return 0

        words = wordList + [beginWord]
        n = len(words)

        def one_apart(a, b):
            diff = 0

            for x, y in zip(a, b):
                if x != y:
                    diff += 1
                    if diff > 1:
                        return False

            return diff == 1

        # Compare every pair of words to build the graph
        graph = [[] for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                if one_apart(words[i], words[j]):
                    graph[i].append(j)
                    graph[j].append(i)

        visited = [False] * n
        visited[n - 1] = True
        queue = deque([(n - 1, 1)])

        while queue:
            i, distance = queue.popleft()

            if words[i] == endWord:
                return distance

            for j in graph[i]:
                if not visited[j]:
                    visited[j] = True
                    queue.append((j, distance + 1))

        return 0
