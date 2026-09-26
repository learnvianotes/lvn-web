class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    String word = null;
}

class Solution {
    private char[][] board;
    private List<String> result;

    public List<String> findWords(char[][] board, String[] words) {
        TrieNode root = new TrieNode();

        // Build Trie from all words
        for (String word : words) {
            TrieNode node = root;

            for (char c : word.toCharArray()) {
                if (!node.children.containsKey(c)) node.children.put(c, new TrieNode());

                node = node.children.get(c);
            }

            node.word = word;
        }

        this.board = board;
        result = new ArrayList<>();

        for (int r = 0; r < board.length; r++) {
            for (int c = 0; c < board[0].length; c++) {
                dfs(r, c, root);
            }
        }

        return result;
    }

    private void dfs(int r, int c, TrieNode node) {
        if (r < 0 || r >= board.length || c < 0 || c >= board[0].length) return;

        char ch = board[r][c];

        if (ch == '#') return;

        if (!node.children.containsKey(ch)) return;

        TrieNode next = node.children.get(ch);

        // Complete word found
        if (next.word != null) {
            result.add(next.word);
            next.word = null;  // prevent duplicates
        }

        board[r][c] = '#';  // mark visited

        dfs(r + 1, c, next);
        dfs(r - 1, c, next);
        dfs(r, c + 1, next);
        dfs(r, c - 1, next);

        board[r][c] = ch;  // restore
    }
}
