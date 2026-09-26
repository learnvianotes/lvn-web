class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    private int[][] heights;
    private int rows, cols;

    public List<List<Integer>> pacificAtlantic(int[][] heights) {
        this.heights = heights;
        rows = heights.length;
        cols = heights[0].length;

        List<int[]> pacific = new ArrayList<>();
        for (int r = 0; r < rows; r++) pacific.add(new int[]{r, 0});
        for (int c = 0; c < cols; c++) pacific.add(new int[]{0, c});

        List<int[]> atlantic = new ArrayList<>();
        for (int r = 0; r < rows; r++) atlantic.add(new int[]{r, cols - 1});
        for (int c = 0; c < cols; c++) atlantic.add(new int[]{rows - 1, c});

        boolean[][] p = bfs(pacific);
        boolean[][] a = bfs(atlantic);

        List<List<Integer>> result = new ArrayList<>();

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (p[r][c] && a[r][c])
                    result.add(Arrays.asList(r, c));

        return result;
    }

    private boolean[][] bfs(List<int[]> starts) {
        boolean[][] visited = new boolean[rows][cols];
        Deque<int[]> queue = new ArrayDeque<>();

        for (int[] cell : starts) {
            visited[cell[0]][cell[1]] = true;
            queue.offer(cell);
        }

        while (!queue.isEmpty()) {
            int[] cell = queue.poll();
            int r = cell[0], c = cell[1];

            for (int[] d : DIRS) {
                int nr = r + d[0], nc = c + d[1];

                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                    !visited[nr][nc] && heights[nr][nc] >= heights[r][c]) {
                    visited[nr][nc] = true;
                    queue.offer(new int[]{nr, nc});
                }
            }
        }

        return visited;
    }
}
