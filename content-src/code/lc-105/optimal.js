var buildTree = function(preorder, inorder) {
    const positions = new Map();
    inorder.forEach((value, i) => positions.set(value, i));

    let preorderIndex = 0;

    const build = (left, right) => {
        if (left > right) return null;

        const rootVal = preorder[preorderIndex++];

        const root = new TreeNode(rootVal);

        const mid = positions.get(rootVal);

        root.left = build(left, mid - 1);
        root.right = build(mid + 1, right);

        return root;
    };

    return build(0, inorder.length - 1);
};
