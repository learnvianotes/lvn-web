class Solution {
    public boolean exist(char[][] board, String word) {
        int rows = board.length;
        int cols = board[0].length;

        Map<Character, Integer> boardCount = new HashMap<>();
        Map<Character, Integer> wordCount = new HashMap<>();
        for (char[] row : board)
            for (char cell : row) boardCount.merge(cell, 1, Integer::sum);
        for (char ch : word.toCharArray()) wordCount.merge(ch, 1, Integer::sum);

        for (Map.Entry<Character, Integer> entry : wordCount.entrySet()) {
            if (boardCount.getOrDefault(entry.getKey(), 0) < entry.getValue()) return false;
        }

        // Start from the rarer character
        char first = word.charAt(0), last = word.charAt(word.length() - 1);
        if (boardCount.getOrDefault(first, 0) > boardCount.getOrDefault(last, 0)) {
            word = new StringBuilder(word).reverse().toString();
        }

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (board[r][c] == word.charAt(0)) {
                    if (dfs(board, word, r, c, 0)) return true;
                }
            }
        }

        return false;
    }

    private boolean dfs(char[][] board, String word, int r, int c, int index) {
        if (index == word.length()) return true;

        if (r < 0 || r >= board.length ||
            c < 0 || c >= board[0].length ||
            board[r][c] != word.charAt(index)) {
            return false;
        }

        char temp = board[r][c];
        board[r][c] = '#';

        boolean found = dfs(board, word, r + 1, c, index + 1) ||
                        dfs(board, word, r - 1, c, index + 1) ||
                        dfs(board, word, r, c + 1, index + 1) ||
                        dfs(board, word, r, c - 1, index + 1);

        board[r][c] = temp;
        return found;
    }
}
