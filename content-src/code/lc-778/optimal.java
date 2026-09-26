class Solution {
    public int swimInWater(int[][] grid) {
        int n = grid.length;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        // {time, r, c}
        PriorityQueue<int[]> minHeap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        minHeap.offer(new int[]{grid[0][0], 0, 0});

        boolean[][] visited = new boolean[n][n];
        visited[0][0] = true;

        while (!minHeap.isEmpty()) {
            int[] top = minHeap.poll();
            int time = top[0], r = top[1], c = top[2];

            if (r == n - 1 && c == n - 1) return time;

            for (int[] d : dirs) {
                int nr = r + d[0], nc = c + d[1];

                if (nr >= 0 && nr < n && nc >= 0 && nc < n && !visited[nr][nc]) {
                    visited[nr][nc] = true;
                    minHeap.offer(new int[]{Math.max(time, grid[nr][nc]), nr, nc});
                }
            }
        }

        return -1;
    }
}
