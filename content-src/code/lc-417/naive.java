class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    private int[][] heights;
    private int rows, cols;
    private boolean[][] visited;

    public List<List<Integer>> pacificAtlantic(int[][] heights) {
        this.heights = heights;
        rows = heights.length;
        cols = heights[0].length;

        List<List<Integer>> result = new ArrayList<>();

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (canReach(r, c, 'P') && canReach(r, c, 'A'))
                    result.add(Arrays.asList(r, c));

        return result;
    }

    private boolean canReach(int r, int c, char target) {
        visited = new boolean[rows][cols];
        return dfs(r, c, target);
    }

    private boolean dfs(int x, int y, char target) {
        if (visited[x][y]) return false;

        if (target == 'P' && (x == 0 || y == 0)) return true;
        if (target == 'A' && (x == rows - 1 || y == cols - 1)) return true;

        visited[x][y] = true;

        for (int[] d : DIRS) {
            int nx = x + d[0], ny = y + d[1];

            if (nx >= 0 && nx < rows && ny >= 0 && ny < cols &&
                heights[nx][ny] <= heights[x][y]) {
                if (dfs(nx, ny, target)) return true;
            }
        }

        return false;
    }
}
