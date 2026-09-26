class Solution {
    private char[][] grid;
    private boolean[][] visited;
    private int rows, cols;

    public int numIslands(char[][] grid) {
        this.grid = grid;
        rows = grid.length;
        cols = grid[0].length;
        visited = new boolean[rows][cols];

        int count = 0;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == '1' && !visited[r][c]) {
                    count++;
                    dfs(r, c);
                }
            }
        }

        return count;
    }

    private void dfs(int r, int c) {
        if (r < 0 || r >= rows || c < 0 || c >= cols ||
            grid[r][c] == '0' || visited[r][c])
            return;

        visited[r][c] = true;

        dfs(r + 1, c);
        dfs(r - 1, c);
        dfs(r, c + 1);
        dfs(r, c - 1);
    }
}
