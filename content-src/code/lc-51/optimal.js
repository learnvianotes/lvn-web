var solveNQueens = function(n) {
    const result = [];

    const board = Array.from({ length: n }, () => new Array(n).fill('.'));

    const columns = new Set();
    const positiveDiagonals = new Set();  // row + col
    const negativeDiagonals = new Set();  // row - col

    const backtrack = (row) => {
        if (row === n) {
            result.push(board.map((r) => r.join('')));
            return;
        }

        for (let col = 0; col < n; col++) {
            if (columns.has(col)) continue;

            if (positiveDiagonals.has(row + col)) continue;

            if (negativeDiagonals.has(row - col)) continue;

            // Place queen
            board[row][col] = 'Q';
            columns.add(col);
            positiveDiagonals.add(row + col);
            negativeDiagonals.add(row - col);

            backtrack(row + 1);

            // Backtrack
            board[row][col] = '.';
            columns.delete(col);
            positiveDiagonals.delete(row + col);
            negativeDiagonals.delete(row - col);
        }
    };

    backtrack(0);

    return result;
};
