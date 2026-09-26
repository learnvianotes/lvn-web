class Solution {
    public void wallsAndGates(int[][] rooms) {
        int rows = rooms.length, cols = rooms[0].length;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        Deque<int[]> queue = new ArrayDeque<>();

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (rooms[r][c] == 0) queue.offer(new int[]{r, c});

        while (!queue.isEmpty()) {
            int[] cell = queue.poll();
            int r = cell[0], c = cell[1];

            for (int[] d : dirs) {
                int nr = r + d[0], nc = c + d[1];

                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                    rooms[nr][nc] == Integer.MAX_VALUE) {
                    rooms[nr][nc] = rooms[r][c] + 1;
                    queue.offer(new int[]{nr, nc});
                }
            }
        }
    }
}
