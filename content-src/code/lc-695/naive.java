class Solution {
    private int[][] grid;
    private boolean[][] visited;
    private int rows, cols;

    public int maxAreaOfIsland(int[][] grid) {
        this.grid = grid;
        rows = grid.length;
        cols = grid[0].length;
        visited = new boolean[rows][cols];

        int answer = 0;

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (grid[r][c] == 1 && !visited[r][c])
                    answer = Math.max(answer, dfs(r, c));

        return answer;
    }

    private int dfs(int r, int c) {
        if (r < 0 || r >= rows || c < 0 || c >= cols ||
            grid[r][c] == 0 || visited[r][c])
            return 0;

        visited[r][c] = true;

        return 1 + dfs(r + 1, c) + dfs(r - 1, c)
                 + dfs(r, c + 1) + dfs(r, c - 1);
    }
}
