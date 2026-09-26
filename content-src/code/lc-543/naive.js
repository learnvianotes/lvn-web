var diameterOfBinaryTree = function(root) {
    const height = (node) => {
        if (!node) return 0;
        return 1 + Math.max(height(node.left), height(node.right));
    };

    if (!root) return 0;

    const leftDiameter = diameterOfBinaryTree(root.left);
    const rightDiameter = diameterOfBinaryTree(root.right);

    const current = height(root.left) + height(root.right);

    return Math.max(current, leftDiameter, rightDiameter);
};
