class Solution {
public:
    bool isValidBST(TreeNode* root) {
        return check(root);
    }

private:
    long long minValue(TreeNode* node) {
        if (!node) return LLONG_MAX;
        return min({(long long)node->val, minValue(node->left), minValue(node->right)});
    }

    long long maxValue(TreeNode* node) {
        if (!node) return LLONG_MIN;
        return max({(long long)node->val, maxValue(node->left), maxValue(node->right)});
    }

    bool check(TreeNode* node) {
        if (!node) return true;

        long long leftMax = maxValue(node->left);
        long long rightMin = minValue(node->right);

        if (node->val <= leftMax || node->val >= rightMin) return false;

        return check(node->left) && check(node->right);
    }
};
