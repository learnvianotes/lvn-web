class Solution {
public:
    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        unordered_map<int, int> positions;
        for (int i = 0; i < (int)inorder.size(); i++) positions[inorder[i]] = i;

        int preorderIndex = 0;

        function<TreeNode*(int, int)> build = [&](int left, int right) -> TreeNode* {
            if (left > right) return nullptr;

            int rootVal = preorder[preorderIndex++];

            TreeNode* root = new TreeNode(rootVal);

            int mid = positions[rootVal];

            root->left = build(left, mid - 1);
            root->right = build(mid + 1, right);

            return root;
        };

        return build(0, (int)inorder.size() - 1);
    }
};
