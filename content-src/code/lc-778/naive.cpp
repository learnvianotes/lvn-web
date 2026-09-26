class Solution {
public:
    int swimInWater(vector<vector<int>>& grid) {
        int n = grid.size();
        int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        // Can we reach the corner using only cells with height <= t?
        auto canReach = [&](int t) {
            if (grid[0][0] > t) return false;

            vector<vector<bool>> visited(n, vector<bool>(n, false));
            queue<pair<int, int>> q;
            q.push({0, 0});
            visited[0][0] = true;

            while (!q.empty()) {
                auto [r, c] = q.front();
                q.pop();

                if (r == n - 1 && c == n - 1) return true;

                for (auto& d : dirs) {
                    int nr = r + d[0], nc = c + d[1];

                    if (nr >= 0 && nr < n && nc >= 0 && nc < n &&
                        !visited[nr][nc] && grid[nr][nc] <= t) {
                        visited[nr][nc] = true;
                        q.push({nr, nc});
                    }
                }
            }

            return false;
        };

        int lo = 0, hi = n * n - 1;

        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;

            if (canReach(mid)) hi = mid;
            else lo = mid + 1;
        }

        return lo;
    }
};
