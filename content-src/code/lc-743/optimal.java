class Solution {
    public int networkDelayTime(int[][] times, int n, int k) {
        List<List<int[]>> graph = new ArrayList<>();
        for (int i = 0; i <= n; i++) graph.add(new ArrayList<>());

        for (int[] t : times)
            graph.get(t[0]).add(new int[]{t[1], t[2]});

        // {time, node}
        PriorityQueue<int[]> minHeap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        minHeap.offer(new int[]{0, k});

        Map<Integer, Integer> distances = new HashMap<>();

        while (!minHeap.isEmpty()) {
            int[] top = minHeap.poll();
            int time = top[0], node = top[1];

            if (distances.containsKey(node)) continue;

            distances.put(node, time);

            for (int[] edge : graph.get(node))
                if (!distances.containsKey(edge[0]))
                    minHeap.offer(new int[]{time + edge[1], edge[0]});
        }

        if (distances.size() == n) return Collections.max(distances.values());

        return -1;
    }
}
