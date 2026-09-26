class Solution {
public:
    bool validTree(int n, vector<vector<int>>& edges) {
        if ((int)edges.size() != n - 1) return false;

        vector<int> parent(n), rank(n, 1);
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
            if (!unite(e[0], e[1])) return false;

        return true;
    }
};
