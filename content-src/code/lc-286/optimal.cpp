class Solution {
public:
    void wallsAndGates(vector<vector<int>>& rooms) {
        int rows = rooms.size(), cols = rooms[0].size();
        int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        queue<pair<int, int>> q;

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (rooms[r][c] == 0) q.push({r, c});

        while (!q.empty()) {
            auto [r, c] = q.front();
            q.pop();

            for (auto& d : dirs) {
                int nr = r + d[0], nc = c + d[1];

                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                    rooms[nr][nc] == 2147483647) {
                    rooms[nr][nc] = rooms[r][c] + 1;
                    q.push({nr, nc});
                }
            }
        }
    }
};
