class Solution {
    private int[][] grid;
    private int rows, cols;

    public int maxAreaOfIsland(int[][] grid) {
        this.grid = grid;
        rows = grid.length;
        cols = grid[0].length;

        int answer = 0;

        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (grid[r][c] == 1)
                    answer = Math.max(answer, dfs(r, c));

        return answer;
    }

    private int dfs(int r, int c) {
        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] == 0)
            return 0;

        grid[r][c] = 0;

        return 1 + dfs(r + 1, c) + dfs(r - 1, c)
                 + dfs(r, c + 1) + dfs(r, c - 1);
    }
}
