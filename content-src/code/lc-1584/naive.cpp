class Solution {
public:
    int minCostConnectPoints(vector<vector<int>>& points) {
        int n = points.size();

        // Build every edge (dist, i, j) and sort them
        vector<array<int, 3>> edges;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int dist = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1]);
                edges.push_back({dist, i, j});
            }
        }
        sort(edges.begin(), edges.end());

        vector<int> parent(n);
        iota(parent.begin(), parent.end(), 0);

        function<int(int)> find = [&](int x) {
            return parent[x] == x ? x : parent[x] = find(parent[x]);
        };

        int totalCost = 0, used = 0;

        for (auto& [dist, i, j] : edges) {
            int rootI = find(i), rootJ = find(j);
            if (rootI == rootJ) continue;

            parent[rootI] = rootJ;
            totalCost += dist;

            if (++used == n - 1) break;
        }

        return totalCost;
    }
};
