class Solution {
public:
    int maxAreaOfIsland(vector<vector<int>>& grid) {
        int rows = grid.size(), cols = grid[0].size();

        function<int(int, int)> dfs = [&](int r, int c) -> int {
            if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] == 0)
                return 0;

            grid[r][c] = 0;

            return 1 + dfs(r + 1, c) + dfs(r - 1, c)
                     + dfs(r, c + 1) + dfs(r, c - 1);
        };

        int answer = 0;

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (grid[r][c] == 1)
                    answer = max(answer, dfs(r, c));

        return answer;
    }
};
