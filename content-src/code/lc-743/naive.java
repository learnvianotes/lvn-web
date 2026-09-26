class Solution {
    public int networkDelayTime(int[][] times, int n, int k) {
        final int INF = Integer.MAX_VALUE;
        int[] dist = new int[n + 1];
        Arrays.fill(dist, INF);
        dist[k] = 0;

        // Relax every edge n - 1 times
        for (int i = 0; i < n - 1; i++) {
            for (int[] t : times) {
                int u = t[0], v = t[1], w = t[2];
                if (dist[u] != INF && dist[u] + w < dist[v])
                    dist[v] = dist[u] + w;
            }
        }

        int answer = 0;
        for (int node = 1; node <= n; node++) {
            if (dist[node] == INF) return -1;
            answer = Math.max(answer, dist[node]);
        }

        return answer;
    }
}
