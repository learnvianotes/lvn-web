class Solution {
public:
    int countComponents(int n, vector<vector<int>>& edges) {
        vector<vector<int>> graph(n);

        for (auto& e : edges) {
            graph[e[0]].push_back(e[1]);
            graph[e[1]].push_back(e[0]);
        }

        vector<bool> visited(n, false);

        function<void(int)> dfs = [&](int node) {
            visited[node] = true;

            for (int neighbor : graph[node])
                if (!visited[neighbor]) dfs(neighbor);
        };

        int components = 0;

        for (int node = 0; node < n; node++) {
            if (!visited[node]) {
                components++;
                dfs(node);
            }
        }

        return components;
    }
};
