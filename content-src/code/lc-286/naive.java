class Solution {
    private static final int INF = 2147483647;
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public void wallsAndGates(int[][] rooms) {
        int rows = rooms.length, cols = rooms[0].length;

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (rooms[r][c] == INF)
                    rooms[r][c] = nearestGate(rooms, r, c);
    }

    // BFS outward from one empty room until the nearest gate is found
    private int nearestGate(int[][] rooms, int sr, int sc) {
        int rows = rooms.length, cols = rooms[0].length;
        boolean[][] visited = new boolean[rows][cols];
        Deque<int[]> queue = new ArrayDeque<>();
        queue.offer(new int[]{sr, sc, 0});
        visited[sr][sc] = true;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int r = cur[0], c = cur[1], dist = cur[2];

            if (rooms[r][c] == 0) return dist;

            for (int[] d : DIRS) {
                int nr = r + d[0], nc = c + d[1];

                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                    !visited[nr][nc] && rooms[nr][nc] != -1) {
                    visited[nr][nc] = true;
                    queue.offer(new int[]{nr, nc, dist + 1});
                }
            }
        }

        return INF;
    }
}
