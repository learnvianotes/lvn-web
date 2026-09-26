class Solution {
    private List<List<Integer>> graph = new ArrayList<>();
    private boolean[] visited;

    public int[] findRedundantConnection(int[][] edges) {
        int n = edges.length;
        for (int i = 0; i <= n; i++) graph.add(new ArrayList<>());

        for (int[] e : edges) {
            int u = e[0], v = e[1];

            visited = new boolean[n + 1];

            if (connected(u, v)) return new int[]{u, v};  // this edge closes a cycle

            graph.get(u).add(v);
            graph.get(v).add(u);
        }

        return new int[0];
    }

    // Is there already a path from u to v?
    private boolean connected(int u, int v) {
        if (u == v) return true;

        visited[u] = true;

        for (int next : graph.get(u))
            if (!visited[next] && connected(next, v)) return true;

        return false;
    }
}
