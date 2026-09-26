class Solution {
public:
    int maxPathSum(TreeNode* root) {
        int answer = INT_MIN;
        dfs(root, answer);
        return answer;
    }

private:
    int dfs(TreeNode* node, int& answer) {
        if (!node) return 0;

        int left = max(0, dfs(node->left, answer));
        int right = max(0, dfs(node->right, answer));

        int current = node->val + left + right;

        answer = max(answer, current);

        return node->val + max(left, right);
    }
};
