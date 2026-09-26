class Solution:
    def orangesRotting(self, grid):
        rows = len(grid)
        cols = len(grid[0])

        minutes = 0

        # Each minute, rescan the whole grid and rot neighbours of rotten oranges
        while True:
            changed = False

            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] != 2:
                        continue

                    for dr, dc in [
                        (1, 0), (-1, 0),
                        (0, 1), (0, -1)
                    ]:
                        nr, nc = r + dr, c + dc

                        if (
                            0 <= nr < rows and
                            0 <= nc < cols and
                            grid[nr][nc] == 1
                        ):
                            grid[nr][nc] = 3  # rots this minute, spreads next minute
                            changed = True

            if not changed:
                break

            for row in grid:
                for c in range(cols):
                    if row[c] == 3:
                        row[c] = 2

            minutes += 1

        for row in grid:
            if 1 in row:
                return -1

        return minutes
