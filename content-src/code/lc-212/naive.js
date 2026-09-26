var findWords = function(board, words) {
    const rows = board.length;
    const cols = board[0].length;
    const result = [];

    const exists = (word) => {
        const dfs = (r, c, index) => {
            if (index === word.length) return true;

            if (
                r < 0 || r >= rows || c < 0 || c >= cols
                || board[r][c] !== word[index]
            ) {
                return false;
            }

            const temp = board[r][c];
            board[r][c] = "#";

            const found = dfs(r + 1, c, index + 1)
                || dfs(r - 1, c, index + 1)
                || dfs(r, c + 1, index + 1)
                || dfs(r, c - 1, index + 1);

            board[r][c] = temp;
            return found;
        };

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (board[r][c] === word[0] && dfs(r, c, 0)) return true;
            }
        }

        return false;
    };

    for (const word of words) {
        if (exists(word)) result.push(word);
    }

    return result;
};
