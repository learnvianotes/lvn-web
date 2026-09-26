class Solution {
public:
    int findCheapestPrice(int n, vector<vector<int>>& flights, int src, int dst, int k) {
        vector<vector<pair<int, int>>> graph(n);
        for (auto& f : flights)
            graph[f[0]].push_back({f[1], f[2]});

        // (cost, node, flights taken) - no visited set, so states can repeat
        priority_queue<array<int, 3>, vector<array<int, 3>>, greater<>> minHeap;
        minHeap.push({0, src, 0});

        while (!minHeap.empty()) {
            auto [cost, node, used] = minHeap.top();
            minHeap.pop();

            if (node == dst) return cost;
            if (used > k) continue;  // at most k stops = k + 1 flights

            for (auto& [next, price] : graph[node])
                minHeap.push({cost + price, next, used + 1});
        }

        return -1;
    }
};
