var buildTree = function(preorder, inorder) {
    if (!preorder.length || !inorder.length) return null;

    const rootVal = preorder[0];
    const root = new TreeNode(rootVal);

    const index = inorder.indexOf(rootVal);

    root.left = buildTree(
        preorder.slice(1, index + 1),
        inorder.slice(0, index)
    );

    root.right = buildTree(
        preorder.slice(index + 1),
        inorder.slice(index + 1)
    );

    return root;
};
