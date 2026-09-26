var solve = function(board) {
    const rows = board.length;
    const cols = board[0].length;
    let visited;

    // Can this 'O' reach the border through other 'O's?
    const reachesBorder = (r, c) => {
        if (r < 0 || r >= rows || c < 0 || c >= cols) return true;
        if (board[r][c] !== "O" || visited[r][c]) return false;

        visited[r][c] = true;

        return reachesBorder(r + 1, c) || reachesBorder(r - 1, c) ||
               reachesBorder(r, c + 1) || reachesBorder(r, c - 1);
    };

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (board[r][c] !== "O") continue;

            visited = Array.from({ length: rows }, () => new Array(cols).fill(false));

            if (!reachesBorder(r, c)) board[r][c] = "X";
        }
    }
};
