class Solution {
public:
    int minCostConnectPoints(vector<vector<int>>& points) {
        int n = points.size();
        vector<bool> visited(n, false);
        int visitedCount = 0;

        // (cost, point_index)
        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<>> minHeap;
        minHeap.push({0, 0});

        int totalCost = 0;

        while (visitedCount < n) {
            auto [cost, u] = minHeap.top();
            minHeap.pop();

            if (visited[u]) continue;

            visited[u] = true;
            visitedCount++;
            totalCost += cost;

            for (int v = 0; v < n; v++) {
                if (!visited[v]) {
                    int dist = abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1]);
                    minHeap.push({dist, v});
                }
            }
        }

        return totalCost;
    }
};
