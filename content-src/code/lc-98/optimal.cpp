class Solution {
public:
    bool isValidBST(TreeNode* root) {
        return dfs(root, LLONG_MIN, LLONG_MAX);
    }

private:
    bool dfs(TreeNode* node, long long low, long long high) {
        if (!node) return true;

        if (!(low < node->val && node->val < high)) return false;

        return dfs(node->left, low, node->val) && dfs(node->right, node->val, high);
    }
};
