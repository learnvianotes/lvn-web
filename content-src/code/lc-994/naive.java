class Solution {
    public int orangesRotting(int[][] grid) {
        int rows = grid.length, cols = grid[0].length;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int minutes = 0;

        // Each minute, rescan the whole grid and rot neighbours of rotten oranges
        while (true) {
            boolean changed = false;

            for (int r = 0; r < rows; r++) {
                for (int c = 0; c < cols; c++) {
                    if (grid[r][c] != 2) continue;

                    for (int[] d : dirs) {
                        int nr = r + d[0], nc = c + d[1];

                        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 1) {
                            grid[nr][nc] = 3;  // rots this minute, spreads next minute
                            changed = true;
                        }
                    }
                }
            }

            if (!changed) break;

            for (int[] row : grid)
                for (int c = 0; c < cols; c++)
                    if (row[c] == 3) row[c] = 2;

            minutes++;
        }

        for (int[] row : grid)
            for (int cell : row)
                if (cell == 1) return -1;

        return minutes;
    }
}
