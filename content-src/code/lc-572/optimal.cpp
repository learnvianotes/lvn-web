class Solution {
public:
    bool isSubtree(TreeNode* root, TreeNode* subRoot) {
        string text, pattern;
        serialize(root, text);
        serialize(subRoot, pattern);

        // KMP algorithm
        int m = pattern.size();
        vector<int> lps(m, 0);

        int j = 0;
        for (int i = 1; i < m; i++) {
            while (j > 0 && pattern[i] != pattern[j]) j = lps[j - 1];

            if (pattern[i] == pattern[j]) j++;

            lps[i] = j;
        }

        j = 0;

        for (int i = 0; i < (int)text.size(); i++) {
            while (j > 0 && text[i] != pattern[j]) j = lps[j - 1];

            if (text[i] == pattern[j]) j++;

            if (j == m) return true;
        }

        return false;
    }

private:
    void serialize(TreeNode* node, string& out) {
        if (!node) {
            out += "#";
            return;
        }

        out += "," + to_string(node->val);
        serialize(node->left, out);
        serialize(node->right, out);
    }
};
