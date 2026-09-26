class Solution {
    private char[][] board;
    private boolean[][] visited;
    private int rows, cols;

    public void solve(char[][] board) {
        this.board = board;
        rows = board.length;
        cols = board[0].length;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (board[r][c] != 'O') continue;

                visited = new boolean[rows][cols];

                if (!reachesBorder(r, c)) board[r][c] = 'X';
            }
        }
    }

    // Can this 'O' reach the border through other 'O's?
    private boolean reachesBorder(int r, int c) {
        if (r < 0 || r >= rows || c < 0 || c >= cols) return true;
        if (board[r][c] != 'O' || visited[r][c]) return false;

        visited[r][c] = true;

        return reachesBorder(r + 1, c) || reachesBorder(r - 1, c) ||
               reachesBorder(r, c + 1) || reachesBorder(r, c - 1);
    }
}
