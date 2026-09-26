class Solution {
public:
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
        vector<TreeNode*> pPath = pathTo(root, p);
        vector<TreeNode*> qPath = pathTo(root, q);

        TreeNode* answer = root;

        for (int i = 0; i < (int)min(pPath.size(), qPath.size()); i++) {
            if (pPath[i] != qPath[i]) break;
            answer = pPath[i];
        }

        return answer;
    }

private:
    vector<TreeNode*> pathTo(TreeNode* node, TreeNode* target) {
        vector<TreeNode*> path;

        while (node) {
            path.push_back(node);

            if (target->val < node->val) node = node->left;
            else if (target->val > node->val) node = node->right;
            else break;
        }

        return path;
    }
};
