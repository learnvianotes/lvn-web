class Solution {
    private List<List<Integer>> graph = new ArrayList<>();
    private boolean[] visited;
    private int count = 0;

    public boolean validTree(int n, int[][] edges) {
        if (edges.length != n - 1) return false;

        for (int i = 0; i < n; i++) graph.add(new ArrayList<>());

        for (int[] e : edges) {
            graph.get(e[0]).add(e[1]);
            graph.get(e[1]).add(e[0]);
        }

        visited = new boolean[n];

        return dfs(0, -1) && count == n;
    }

    private boolean dfs(int node, int parent) {
        if (visited[node]) return false;

        visited[node] = true;
        count++;

        for (int neighbor : graph.get(node)) {
            if (neighbor == parent) continue;
            if (!dfs(neighbor, node)) return false;
        }

        return true;
    }
}
