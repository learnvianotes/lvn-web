class Solution {
    public List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        char[][] board = new char[n][n];
        for (char[] row : board) Arrays.fill(row, '.');

        backtrack(0, n, board, result);
        return result;
    }

    private boolean isSafe(int row, int col, int n, char[][] board) {
        // Check column
        for (int r = 0; r < row; r++) {
            if (board[r][col] == 'Q') return false;
        }

        // Check upper-left diagonal
        for (int r = row - 1, c = col - 1; r >= 0 && c >= 0; r--, c--) {
            if (board[r][c] == 'Q') return false;
        }

        // Check upper-right diagonal
        for (int r = row - 1, c = col + 1; r >= 0 && c < n; r--, c++) {
            if (board[r][c] == 'Q') return false;
        }

        return true;
    }

    private void backtrack(int row, int n, char[][] board, List<List<String>> result) {
        if (row == n) {
            List<String> snapshot = new ArrayList<>();
            for (char[] r : board) snapshot.add(new String(r));
            result.add(snapshot);
            return;
        }

        for (int col = 0; col < n; col++) {
            if (isSafe(row, col, n, board)) {
                board[row][col] = 'Q';
                backtrack(row + 1, n, board, result);
                board[row][col] = '.';
            }
        }
    }
}
