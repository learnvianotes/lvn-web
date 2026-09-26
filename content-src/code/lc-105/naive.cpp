class Solution {
public:
    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        if (preorder.empty() || inorder.empty()) return nullptr;

        int rootVal = preorder[0];
        TreeNode* root = new TreeNode(rootVal);

        int index = find(inorder.begin(), inorder.end(), rootVal) - inorder.begin();

        vector<int> leftPre(preorder.begin() + 1, preorder.begin() + index + 1);
        vector<int> leftIn(inorder.begin(), inorder.begin() + index);
        root->left = buildTree(leftPre, leftIn);

        vector<int> rightPre(preorder.begin() + index + 1, preorder.end());
        vector<int> rightIn(inorder.begin() + index + 1, inorder.end());
        root->right = buildTree(rightPre, rightIn);

        return root;
    }
};
