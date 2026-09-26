class Solution {
public:
    vector<vector<int>> kClosest(vector<vector<int>>& points, int k) {
        priority_queue<array<int, 3>> heap;  // max-heap by distance

        for (auto& p : points) {
            int x = p[0], y = p[1];
            int distance = x * x + y * y;

            heap.push({distance, x, y});

            if ((int)heap.size() > k) heap.pop();
        }

        vector<vector<int>> result;
        while (!heap.empty()) {
            auto [_, x, y] = heap.top();
            heap.pop();
            result.push_back({x, y});
        }

        return result;
    }
};
