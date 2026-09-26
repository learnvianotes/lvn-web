var isBalanced = function(root) {
    const height = (node) => {
        if (!node) return 0;
        return 1 + Math.max(height(node.left), height(node.right));
    };

    if (!root) return true;

    const left = height(root.left);
    const right = height(root.right);

    if (Math.abs(left - right) > 1) return false;

    return isBalanced(root.left) && isBalanced(root.right);
};
