var exist = function(board, word) {
    const rows = board.length;
    const cols = board[0].length;

    const boardCount = new Map();
    const wordCount = new Map();
    for (const row of board)
        for (const cell of row) boardCount.set(cell, (boardCount.get(cell) || 0) + 1);
    for (const ch of word) wordCount.set(ch, (wordCount.get(ch) || 0) + 1);

    for (const [ch, count] of wordCount) {
        if ((boardCount.get(ch) || 0) < count) return false;
    }

    // Start from the rarer character
    if ((boardCount.get(word[0]) || 0) > (boardCount.get(word[word.length - 1]) || 0)) {
        word = [...word].reverse().join('');
    }

    const dfs = (r, c, index) => {
        if (index === word.length) return true;

        if (
            r < 0 || r >= rows ||
            c < 0 || c >= cols ||
            board[r][c] !== word[index]
        ) {
            return false;
        }

        const temp = board[r][c];
        board[r][c] = '#';

        const found =
            dfs(r + 1, c, index + 1) ||
            dfs(r - 1, c, index + 1) ||
            dfs(r, c + 1, index + 1) ||
            dfs(r, c - 1, index + 1);

        board[r][c] = temp;
        return found;
    };

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (board[r][c] === word[0]) {
                if (dfs(r, c, 0)) return true;
            }
        }
    }

    return false;
};
