class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public int swimInWater(int[][] grid) {
        int n = grid.length;
        int lo = 0, hi = n * n - 1;

        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;

            if (canReach(grid, mid)) hi = mid;
            else lo = mid + 1;
        }

        return lo;
    }

    // Can we reach the corner using only cells with height <= t?
    private boolean canReach(int[][] grid, int t) {
        int n = grid.length;
        if (grid[0][0] > t) return false;

        boolean[][] visited = new boolean[n][n];
        Deque<int[]> queue = new ArrayDeque<>();
        queue.offer(new int[]{0, 0});
        visited[0][0] = true;

        while (!queue.isEmpty()) {
            int[] cell = queue.poll();
            int r = cell[0], c = cell[1];

            if (r == n - 1 && c == n - 1) return true;

            for (int[] d : DIRS) {
                int nr = r + d[0], nc = c + d[1];

                if (nr >= 0 && nr < n && nc >= 0 && nc < n &&
                    !visited[nr][nc] && grid[nr][nc] <= t) {
                    visited[nr][nc] = true;
                    queue.offer(new int[]{nr, nc});
                }
            }
        }

        return false;
    }
}
