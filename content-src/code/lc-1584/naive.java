class Solution {
    private int[] parent;

    public int minCostConnectPoints(int[][] points) {
        int n = points.length;

        // Build every edge (dist, i, j) and sort them
        List<int[]> edges = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int dist = Math.abs(points[i][0] - points[j][0]) + Math.abs(points[i][1] - points[j][1]);
                edges.add(new int[]{dist, i, j});
            }
        }
        edges.sort((a, b) -> Integer.compare(a[0], b[0]));

        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;

        int totalCost = 0, used = 0;

        for (int[] e : edges) {
            int rootI = find(e[1]), rootJ = find(e[2]);
            if (rootI == rootJ) continue;

            parent[rootI] = rootJ;
            totalCost += e[0];

            if (++used == n - 1) break;
        }

        return totalCost;
    }

    private int find(int x) {
        while (x != parent[x]) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }
}
