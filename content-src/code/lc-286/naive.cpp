class Solution {
public:
    void wallsAndGates(vector<vector<int>>& rooms) {
        const int INF = 2147483647;
        int rows = rooms.size(), cols = rooms[0].size();
        int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        // BFS outward from one empty room until the nearest gate is found
        auto nearestGate = [&](int sr, int sc) {
            vector<vector<bool>> visited(rows, vector<bool>(cols, false));
            queue<tuple<int, int, int>> q;
            q.push({sr, sc, 0});
            visited[sr][sc] = true;

            while (!q.empty()) {
                auto [r, c, dist] = q.front();
                q.pop();

                if (rooms[r][c] == 0) return dist;

                for (auto& d : dirs) {
                    int nr = r + d[0], nc = c + d[1];

                    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                        !visited[nr][nc] && rooms[nr][nc] != -1) {
                        visited[nr][nc] = true;
                        q.push({nr, nc, dist + 1});
                    }
                }
            }

            return INF;
        };

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (rooms[r][c] == INF)
                    rooms[r][c] = nearestGate(r, c);
    }
};
