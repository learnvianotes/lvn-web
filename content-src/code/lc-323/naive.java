class Solution {
    private List<List<Integer>> graph = new ArrayList<>();
    private boolean[] visited;

    public int countComponents(int n, int[][] edges) {
        for (int i = 0; i < n; i++) graph.add(new ArrayList<>());

        for (int[] e : edges) {
            graph.get(e[0]).add(e[1]);
            graph.get(e[1]).add(e[0]);
        }

        visited = new boolean[n];
        int components = 0;

        for (int node = 0; node < n; node++) {
            if (!visited[node]) {
                components++;
                dfs(node);
            }
        }

        return components;
    }

    private void dfs(int node) {
        visited[node] = true;

        for (int neighbor : graph.get(node))
            if (!visited[neighbor]) dfs(neighbor);
    }
}
