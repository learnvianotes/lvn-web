class Solution {
public:
    vector<vector<int>> pacificAtlantic(vector<vector<int>>& heights) {
        int rows = heights.size(), cols = heights[0].size();
        int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        auto bfs = [&](const vector<pair<int, int>>& starts) {
            vector<vector<bool>> visited(rows, vector<bool>(cols, false));
            queue<pair<int, int>> q;

            for (auto& [r, c] : starts) {
                visited[r][c] = true;
                q.push({r, c});
            }

            while (!q.empty()) {
                auto [r, c] = q.front();
                q.pop();

                for (auto& d : dirs) {
                    int nr = r + d[0], nc = c + d[1];

                    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                        !visited[nr][nc] && heights[nr][nc] >= heights[r][c]) {
                        visited[nr][nc] = true;
                        q.push({nr, nc});
                    }
                }
            }

            return visited;
        };

        vector<pair<int, int>> pacific, atlantic;

        for (int r = 0; r < rows; r++) pacific.push_back({r, 0});
        for (int c = 0; c < cols; c++) pacific.push_back({0, c});

        for (int r = 0; r < rows; r++) atlantic.push_back({r, cols - 1});
        for (int c = 0; c < cols; c++) atlantic.push_back({rows - 1, c});

        auto p = bfs(pacific);
        auto a = bfs(atlantic);

        vector<vector<int>> result;

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (p[r][c] && a[r][c])
                    result.push_back({r, c});

        return result;
    }
};
