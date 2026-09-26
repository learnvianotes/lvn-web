class Solution {
public:
    int countComponents(int n, vector<vector<int>>& edges) {
        vector<int> parent(n), rank(n, 1);
        iota(parent.begin(), parent.end(), 0);
        int components = n;

        auto find = [&](int x) {
            while (x != parent[x]) {
                parent[x] = parent[parent[x]];
                x = parent[x];
            }
            return x;
        };

        auto unite = [&](int a, int b) {
            int rootA = find(a), rootB = find(b);

            if (rootA == rootB) return;

            if (rank[rootA] < rank[rootB]) swap(rootA, rootB);

            parent[rootB] = rootA;
            rank[rootA] += rank[rootB];

            components--;
        };

        for (auto& e : edges) unite(e[0], e[1]);

        return components;
    }
};
