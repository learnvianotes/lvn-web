var solveNQueens = function(n) {
    const result = [];
    const board = Array.from({ length: n }, () => new Array(n).fill('.'));

    const isSafe = (row, col) => {
        // Check column
        for (let r = 0; r < row; r++) {
            if (board[r][col] === 'Q') return false;
        }

        // Check upper-left diagonal
        for (let r = row - 1, c = col - 1; r >= 0 && c >= 0; r--, c--) {
            if (board[r][c] === 'Q') return false;
        }

        // Check upper-right diagonal
        for (let r = row - 1, c = col + 1; r >= 0 && c < n; r--, c++) {
            if (board[r][c] === 'Q') return false;
        }

        return true;
    };

    const backtrack = (row) => {
        if (row === n) {
            result.push(board.map((r) => r.join('')));
            return;
        }

        for (let col = 0; col < n; col++) {
            if (isSafe(row, col)) {
                board[row][col] = 'Q';
                backtrack(row + 1);
                board[row][col] = '.';
            }
        }
    };

    backtrack(0);
    return result;
};
