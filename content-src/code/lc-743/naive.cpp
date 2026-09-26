class Solution {
public:
    int networkDelayTime(vector<vector<int>>& times, int n, int k) {
        const int INF = INT_MAX;
        vector<int> dist(n + 1, INF);
        dist[k] = 0;

        // Relax every edge n - 1 times
        for (int i = 0; i < n - 1; i++) {
            for (auto& t : times) {
                int u = t[0], v = t[1], w = t[2];
                if (dist[u] != INF && dist[u] + w < dist[v])
                    dist[v] = dist[u] + w;
            }
        }

        int answer = 0;
        for (int node = 1; node <= n; node++) {
            if (dist[node] == INF) return -1;
            answer = max(answer, dist[node]);
        }

        return answer;
    }
};
