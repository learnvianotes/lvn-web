from collections import deque

class Solution:
    def swimInWater(self, grid):
        n = len(grid)

        # Can we reach the corner using only cells with height <= t?
        def can_reach(t):
            if grid[0][0] > t:
                return False

            visited = {(0, 0)}
            queue = deque([(0, 0)])

            while queue:
                r, c = queue.popleft()

                if r == n - 1 and c == n - 1:
                    return True

                for dr, dc in [
                    (1, 0), (-1, 0),
                    (0, 1), (0, -1)
                ]:
                    nr, nc = r + dr, c + dc

                    if (
                        0 <= nr < n and
                        0 <= nc < n and
                        (nr, nc) not in visited and
                        grid[nr][nc] <= t
                    ):
                        visited.add((nr, nc))
                        queue.append((nr, nc))

            return False

        lo, hi = 0, n * n - 1

        while lo < hi:
            mid = (lo + hi) // 2

            if can_reach(mid):
                hi = mid
            else:
                lo = mid + 1

        return lo
