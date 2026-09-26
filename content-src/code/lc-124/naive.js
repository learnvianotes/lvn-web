var maxPathSum = function(root) {
    const gain = (node) => {
        if (!node) return 0;

        return node.val + Math.max(0, gain(node.left), gain(node.right));
    };

    const path = (node) => {
        if (!node) return -Infinity;

        const left = gain(node.left);
        const right = gain(node.right);

        const current = node.val + Math.max(0, left) + Math.max(0, right);

        return Math.max(current, path(node.left), path(node.right));
    };

    return path(root);
};
