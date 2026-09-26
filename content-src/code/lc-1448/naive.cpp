class Solution {
public:
    int goodNodes(TreeNode* root) {
        vector<int> path;
        return dfs(root, path);
    }

private:
    int dfs(TreeNode* node, vector<int>& path) {
        if (!node) return 0;

        path.push_back(node->val);

        int count = 0;
        if (node->val == *max_element(path.begin(), path.end())) count++;

        count += dfs(node->left, path);
        count += dfs(node->right, path);

        path.pop_back();
        return count;
    }
};
