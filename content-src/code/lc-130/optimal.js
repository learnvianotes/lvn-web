var solve = function(board) {
    const rows = board.length;
    const cols = board[0].length;

    const dfs = (r, c) => {
        if (
            r < 0 || r >= rows ||
            c < 0 || c >= cols ||
            board[r][c] !== "O"
        ) return;

        board[r][c] = "#";

        dfs(r + 1, c);
        dfs(r - 1, c);
        dfs(r, c + 1);
        dfs(r, c - 1);
    };

    // Mark boundary-connected O's
    for (let r = 0; r < rows; r++) {
        dfs(r, 0);
        dfs(r, cols - 1);
    }

    for (let c = 0; c < cols; c++) {
        dfs(0, c);
        dfs(rows - 1, c);
    }

    // Capture surrounded regions
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (board[r][c] === "O") board[r][c] = "X";
            else if (board[r][c] === "#") board[r][c] = "O";
        }
    }
};
