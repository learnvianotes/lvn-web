class Solution {
    private int[] parent, rank;
    private int components;

    public int countComponents(int n, int[][] edges) {
        parent = new int[n];
        rank = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            rank[i] = 1;
        }
        components = n;

        for (int[] e : edges) union(e[0], e[1]);

        return components;
    }

    private int find(int x) {
        while (x != parent[x]) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    private void union(int a, int b) {
        int rootA = find(a), rootB = find(b);

        if (rootA == rootB) return;

        if (rank[rootA] < rank[rootB]) {
            int tmp = rootA; rootA = rootB; rootB = tmp;
        }

        parent[rootB] = rootA;
        rank[rootA] += rank[rootB];

        components--;
    }
}
