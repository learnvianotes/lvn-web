class Solution {
    public int[][] kClosest(int[][] points, int k) {
        // max-heap by distance: {distance, x, y}
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> Integer.compare(b[0], a[0]));

        for (int[] p : points) {
            int x = p[0], y = p[1];
            int distance = x * x + y * y;

            heap.offer(new int[]{distance, x, y});

            if (heap.size() > k) heap.poll();
        }

        int[][] result = new int[heap.size()][];
        int i = 0;
        for (int[] entry : heap) {
            result[i++] = new int[]{entry[1], entry[2]};
        }

        return result;
    }
}
