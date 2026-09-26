from collections import deque

class Solution:
    def wallsAndGates(self, rooms):
        INF = 2147483647
        rows = len(rooms)
        cols = len(rooms[0])

        # BFS outward from one empty room until the nearest gate is found
        def nearest_gate(sr, sc):
            visited = {(sr, sc)}
            queue = deque([(sr, sc, 0)])

            while queue:
                r, c, dist = queue.popleft()

                if rooms[r][c] == 0:
                    return dist

                for dr, dc in [
                    (1, 0), (-1, 0),
                    (0, 1), (0, -1)
                ]:
                    nr, nc = r + dr, c + dc

                    if (
                        0 <= nr < rows
                        and 0 <= nc < cols
                        and (nr, nc) not in visited
                        and rooms[nr][nc] != -1
                    ):
                        visited.add((nr, nc))
                        queue.append((nr, nc, dist + 1))

            return INF

        for r in range(rows):
            for c in range(cols):
                if rooms[r][c] == INF:
                    rooms[r][c] = nearest_gate(r, c)
