class Solution {
public:
    int orangesRotting(vector<vector<int>>& grid) {
        int rows = grid.size(), cols = grid[0].size();
        int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int minutes = 0;

        // Each minute, rescan the whole grid and rot neighbours of rotten oranges
        while (true) {
            bool changed = false;

            for (int r = 0; r < rows; r++) {
                for (int c = 0; c < cols; c++) {
                    if (grid[r][c] != 2) continue;

                    for (auto& d : dirs) {
                        int nr = r + d[0], nc = c + d[1];

                        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 1) {
                            grid[nr][nc] = 3;  // rots this minute, spreads next minute
                            changed = true;
                        }
                    }
                }
            }

            if (!changed) break;

            for (auto& row : grid)
                for (int& cell : row)
                    if (cell == 3) cell = 2;

            minutes++;
        }

        for (auto& row : grid)
            for (int cell : row)
                if (cell == 1) return -1;

        return minutes;
    }
};
