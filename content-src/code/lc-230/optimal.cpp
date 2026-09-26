class Solution {
public:
    int kthSmallest(TreeNode* root, int k) {
        stack<TreeNode*> st;
        TreeNode* node = root;

        while (true) {
            while (node) {
                st.push(node);
                node = node->left;
            }

            node = st.top();
            st.pop();
            k--;

            if (k == 0) return node->val;

            node = node->right;
        }
    }
};
