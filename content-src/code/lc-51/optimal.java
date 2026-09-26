class Solution {
    private List<List<String>> result = new ArrayList<>();
    private char[][] board;

    private Set<Integer> columns = new HashSet<>();
    private Set<Integer> positiveDiagonals = new HashSet<>();  // row + col
    private Set<Integer> negativeDiagonals = new HashSet<>();  // row - col

    public List<List<String>> solveNQueens(int n) {
        board = new char[n][n];
        for (char[] row : board) Arrays.fill(row, '.');

        backtrack(0, n);

        return result;
    }

    private void backtrack(int row, int n) {
        if (row == n) {
            List<String> snapshot = new ArrayList<>();
            for (char[] r : board) snapshot.add(new String(r));
            result.add(snapshot);
            return;
        }

        for (int col = 0; col < n; col++) {
            if (columns.contains(col)) continue;

            if (positiveDiagonals.contains(row + col)) continue;

            if (negativeDiagonals.contains(row - col)) continue;

            // Place queen
            board[row][col] = 'Q';
            columns.add(col);
            positiveDiagonals.add(row + col);
            negativeDiagonals.add(row - col);

            backtrack(row + 1, n);

            // Backtrack
            board[row][col] = '.';
            columns.remove(col);
            positiveDiagonals.remove(row + col);
            negativeDiagonals.remove(row - col);
        }
    }
}
