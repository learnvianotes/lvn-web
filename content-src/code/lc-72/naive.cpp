class Solution {
public:
    int minDistance(string word1, string word2) {
        return dfs(word1, word2, 0, 0);
    }

private:
    int dfs(const string& word1, const string& word2, int i, int j) {
        if (i == (int)word1.size()) return word2.size() - j;
        if (j == (int)word2.size()) return word1.size() - i;

        if (word1[i] == word2[j]) return dfs(word1, word2, i + 1, j + 1);

        int insert = dfs(word1, word2, i, j + 1);
        int remove = dfs(word1, word2, i + 1, j);
        int replace = dfs(word1, word2, i + 1, j + 1);

        return 1 + min({insert, remove, replace});
    }
};
