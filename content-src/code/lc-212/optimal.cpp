struct TrieNode {
    unordered_map<char, TrieNode*> children;
    string word;  // empty means "no word ends here"
};

class Solution {
public:
    vector<string> findWords(vector<vector<char>>& board, vector<string>& words) {
        TrieNode* root = new TrieNode();

        // Build Trie from all words
        for (const string& word : words) {
            TrieNode* node = root;

            for (char c : word) {
                if (!node->children.count(c)) node->children[c] = new TrieNode();

                node = node->children[c];
            }

            node->word = word;
        }

        vector<string> result;

        for (int r = 0; r < (int)board.size(); r++) {
            for (int c = 0; c < (int)board[0].size(); c++) {
                dfs(board, r, c, root, result);
            }
        }

        return result;
    }

private:
    void dfs(vector<vector<char>>& board, int r, int c, TrieNode* node, vector<string>& result) {
        if (r < 0 || r >= (int)board.size() || c < 0 || c >= (int)board[0].size()) return;

        char ch = board[r][c];

        if (ch == '#') return;

        if (!node->children.count(ch)) return;

        TrieNode* next = node->children[ch];

        // Complete word found
        if (!next->word.empty()) {
            result.push_back(next->word);
            next->word.clear();  // prevent duplicates
        }

        board[r][c] = '#';  // mark visited

        dfs(board, r + 1, c, next, result);
        dfs(board, r - 1, c, next, result);
        dfs(board, r, c + 1, next, result);
        dfs(board, r, c - 1, next, result);

        board[r][c] = ch;  // restore
    }
};
