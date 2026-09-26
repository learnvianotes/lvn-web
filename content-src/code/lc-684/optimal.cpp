class Solution {
public:
    vector<int> findRedundantConnection(vector<vector<int>>& edges) {
        int n = edges.size();
        vector<int> parent(n + 1), rank(n + 1, 1);
        iota(parent.begin(), parent.end(), 0);

        auto find = [&](int x) {
            while (x != parent[x]) {
                parent[x] = parent[parent[x]];
                x = parent[x];
            }
            return x;
        };

        auto unite = [&](int a, int b) {
            int rootA = find(a), rootB = find(b);

            if (rootA == rootB) return false;

            if (rank[rootA] < rank[rootB]) swap(rootA, rootB);

            parent[rootB] = rootA;
            rank[rootA] += rank[rootB];

            return true;
        };

        for (auto& e : edges)
            if (!unite(e[0], e[1])) return {e[0], e[1]};

        return {};
    }
};
