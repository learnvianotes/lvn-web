class Solution {
    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        List<List<int[]>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) graph.add(new ArrayList<>());
        for (int[] f : flights)
            graph.get(f[0]).add(new int[]{f[1], f[2]});

        // {cost, node, flights taken} - no visited set, so states can repeat
        PriorityQueue<int[]> minHeap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        minHeap.offer(new int[]{0, src, 0});

        while (!minHeap.isEmpty()) {
            int[] top = minHeap.poll();
            int cost = top[0], node = top[1], used = top[2];

            if (node == dst) return cost;
            if (used > k) continue;  // at most k stops = k + 1 flights

            for (int[] edge : graph.get(node))
                minHeap.offer(new int[]{cost + edge[1], edge[0], used + 1});
        }

        return -1;
    }
}
