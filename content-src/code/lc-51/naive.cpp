class Solution {
public:
    vector<vector<string>> solveNQueens(int n) {
        vector<vector<string>> result;
        vector<string> board(n, string(n, '.'));
        backtrack(0, n, board, result);
        return result;
    }

private:
    bool isSafe(int row, int col, int n, vector<string>& board) {
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

    void backtrack(int row, int n, vector<string>& board, vector<vector<string>>& result) {
        if (row == n) {
            result.push_back(board);
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
};
