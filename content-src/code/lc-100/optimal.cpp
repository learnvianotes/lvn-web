class Solution {
public:
    bool isSameTree(TreeNode* p, TreeNode* q) {
        queue<pair<TreeNode*, TreeNode*>> pairs;
        pairs.push({p, q});

        while (!pairs.empty()) {
            auto [a, b] = pairs.front();
            pairs.pop();

            if (!a && !b) continue;

            if (!a || !b) return false;

            if (a->val != b->val) return false;

            pairs.push({a->left, b->left});
            pairs.push({a->right, b->right});
        }

        return true;
    }
};
