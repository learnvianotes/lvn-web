class Solution {
    private char[][] board;
    private int rows, cols;

    public void solve(char[][] board) {
        this.board = board;
        rows = board.length;
        cols = board[0].length;

        // Mark boundary-connected O's
        for (int r = 0; r < rows; r++) {
            dfs(r, 0);
            dfs(r, cols - 1);
        }

        for (int c = 0; c < cols; c++) {
            dfs(0, c);
            dfs(rows - 1, c);
        }

        // Capture surrounded regions
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (board[r][c] == 'O') board[r][c] = 'X';
                else if (board[r][c] == '#') board[r][c] = 'O';
            }
        }
    }

    private void dfs(int r, int c) {
        if (r < 0 || r >= rows || c < 0 || c >= cols || board[r][c] != 'O')
            return;

        board[r][c] = '#';

        dfs(r + 1, c);
        dfs(r - 1, c);
        dfs(r, c + 1);
        dfs(r, c - 1);
    }
}
