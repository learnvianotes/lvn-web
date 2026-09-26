var kthSmallest = function(root, k) {
    const values = [];

    const inorder = (node) => {
        if (!node) return;

        inorder(node.left);
        values.push(node.val);
        inorder(node.right);
    };

    inorder(root);

    return values[k - 1];
};
