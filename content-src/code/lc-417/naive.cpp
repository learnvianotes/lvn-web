class Solution {
public:
    vector<vector<int>> pacificAtlantic(vector<vector<int>>& heights) {
        int rows = heights.size(), cols = heights[0].size();
        int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        auto canReach = [&](int r, int c, char target) {
            vector<vector<bool>> visited(rows, vector<bool>(cols, false));

            function<bool(int, int)> dfs = [&](int x, int y) -> bool {
                if (visited[x][y]) return false;

                if (target == 'P' && (x == 0 || y == 0)) return true;
                if (target == 'A' && (x == rows - 1 || y == cols - 1)) return true;

                visited[x][y] = true;

                for (auto& d : dirs) {
                    int nx = x + d[0], ny = y + d[1];

                    if (nx >= 0 && nx < rows && ny >= 0 && ny < cols &&
                        heights[nx][ny] <= heights[x][y]) {
                        if (dfs(nx, ny)) return true;
                    }
                }

                return false;
            };

            return dfs(r, c);
        };

        vector<vector<int>> result;

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (canReach(r, c, 'P') && canReach(r, c, 'A'))
                    result.push_back({r, c});

        return result;
    }
};
