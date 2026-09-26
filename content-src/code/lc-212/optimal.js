class TrieNode {
    constructor() {
        this.children = new Map();
        this.word = null;
    }
}

var findWords = function(board, words) {
    const root = new TrieNode();

    // Build Trie from all words
    for (const word of words) {
        let node = root;

        for (const char of word) {
            if (!node.children.has(char)) node.children.set(char, new TrieNode());

            node = node.children.get(char);
        }

        node.word = word;
    }

    const rows = board.length;
    const cols = board[0].length;
    const result = [];

    const dfs = (r, c, node) => {
        if (r < 0 || r >= rows || c < 0 || c >= cols) return;

        const char = board[r][c];

        if (char === "#") return;

        if (!node.children.has(char)) return;

        const nextNode = node.children.get(char);

        // Complete word found
        if (nextNode.word !== null) {
            result.push(nextNode.word);
            nextNode.word = null; // prevent duplicates
        }

        board[r][c] = "#"; // mark visited

        dfs(r + 1, c, nextNode);
        dfs(r - 1, c, nextNode);
        dfs(r, c + 1, nextNode);
        dfs(r, c - 1, nextNode);

        board[r][c] = char; // restore
    };

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            dfs(r, c, root);
        }
    }

    return result;
};
