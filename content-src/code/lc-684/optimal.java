class Solution {
    private int[] parent, rank;

    public int[] findRedundantConnection(int[][] edges) {
        int n = edges.length;
        parent = new int[n + 1];
        rank = new int[n + 1];
        for (int i = 0; i <= n; i++) {
            parent[i] = i;
            rank[i] = 1;
        }

        for (int[] e : edges)
            if (!union(e[0], e[1])) return new int[]{e[0], e[1]};

        return new int[0];
    }

    private int find(int x) {
        while (x != parent[x]) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    private boolean union(int a, int b) {
        int rootA = find(a), rootB = find(b);

        if (rootA == rootB) return false;

        if (rank[rootA] < rank[rootB]) {
            int tmp = rootA; rootA = rootB; rootB = tmp;
        }

        parent[rootB] = rootA;
        rank[rootA] += rank[rootB];

        return true;
    }
}
