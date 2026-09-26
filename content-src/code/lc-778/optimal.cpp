class Solution {
public:
    int swimInWater(vector<vector<int>>& grid) {
        int n = grid.size();
        int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        // (time, r, c)
        priority_queue<array<int, 3>, vector<array<int, 3>>, greater<>> minHeap;
        minHeap.push({grid[0][0], 0, 0});

        vector<vector<bool>> visited(n, vector<bool>(n, false));
        visited[0][0] = true;

        while (!minHeap.empty()) {
            auto [time, r, c] = minHeap.top();
            minHeap.pop();

            if (r == n - 1 && c == n - 1) return time;

            for (auto& d : dirs) {
                int nr = r + d[0], nc = c + d[1];

                if (nr >= 0 && nr < n && nc >= 0 && nc < n && !visited[nr][nc]) {
                    visited[nr][nc] = true;
                    minHeap.push({max(time, grid[nr][nc]), nr, nc});
                }
            }
        }

        return -1;
    }
};
