class Solution {
public:
    vector<int> findRedundantConnection(vector<vector<int>>& edges) {
        int n = edges.size();
        vector<vector<int>> graph(n + 1);
        vector<bool> visited;

        // Is there already a path from u to v?
        function<bool(int, int)> connected = [&](int u, int v) -> bool {
            if (u == v) return true;

            visited[u] = true;

            for (int next : graph[u])
                if (!visited[next] && connected(next, v)) return true;

            return false;
        };

        for (auto& e : edges) {
            int u = e[0], v = e[1];

            visited.assign(n + 1, false);

            if (connected(u, v)) return {u, v};  // this edge closes a cycle

            graph[u].push_back(v);
            graph[v].push_back(u);
        }

        return {};
    }
};
