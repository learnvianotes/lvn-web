class Solution {
public:
    int maxPathSum(TreeNode* root) {
        return path(root);
    }

private:
    int gain(TreeNode* node) {
        if (!node) return 0;

        return node->val + max({0, gain(node->left), gain(node->right)});
    }

    int path(TreeNode* node) {
        if (!node) return INT_MIN;

        int left = gain(node->left);
        int right = gain(node->right);

        int current = node->val + max(0, left) + max(0, right);

        return max({current, path(node->left), path(node->right)});
    }
};
