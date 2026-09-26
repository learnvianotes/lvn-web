class Solution {
public:
    int networkDelayTime(vector<vector<int>>& times, int n, int k) {
        vector<vector<pair<int, int>>> graph(n + 1);

        for (auto& t : times)
            graph[t[0]].push_back({t[1], t[2]});

        // (time, node)
        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<>> minHeap;
        minHeap.push({0, k});

        vector<int> distances(n + 1, -1);
        int reached = 0, answer = 0;

        while (!minHeap.empty()) {
            auto [time, node] = minHeap.top();
            minHeap.pop();

            if (distances[node] != -1) continue;

            distances[node] = time;
            reached++;
            answer = max(answer, time);

            for (auto& [neighbor, weight] : graph[node])
                if (distances[neighbor] == -1)
                    minHeap.push({time + weight, neighbor});
        }

        return reached == n ? answer : -1;
    }
};
