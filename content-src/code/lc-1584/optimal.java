class Solution {
    public int minCostConnectPoints(int[][] points) {
        int n = points.length;
        boolean[] visited = new boolean[n];
        int visitedCount = 0;

        // {cost, point_index}
        PriorityQueue<int[]> minHeap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        minHeap.offer(new int[]{0, 0});

        int totalCost = 0;

        while (visitedCount < n) {
            int[] top = minHeap.poll();
            int cost = top[0], u = top[1];

            if (visited[u]) continue;

            visited[u] = true;
            visitedCount++;
            totalCost += cost;

            for (int v = 0; v < n; v++) {
                if (!visited[v]) {
                    int dist = Math.abs(points[u][0] - points[v][0]) + Math.abs(points[u][1] - points[v][1]);
                    minHeap.offer(new int[]{dist, v});
                }
            }
        }

        return totalCost;
    }
}
