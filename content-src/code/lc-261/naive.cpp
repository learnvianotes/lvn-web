class Solution {
public:
    bool validTree(int n, vector<vector<int>>& edges) {
        if ((int)edges.size() != n - 1) return false;

        vector<vector<int>> graph(n);

        for (auto& e : edges) {
            graph[e[0]].push_back(e[1]);
            graph[e[1]].push_back(e[0]);
        }

        vector<bool> visited(n, false);
        int count = 0;

        function<bool(int, int)> dfs = [&](int node, int parent) -> bool {
            if (visited[node]) return false;

            visited[node] = true;
            count++;

            for (int neighbor : graph[node]) {
                if (neighbor == parent) continue;
                if (!dfs(neighbor, node)) return false;
            }

            return true;
        };

        return dfs(0, -1) && count == n;
    }
};
