var isValidBST = function(root) {
    const minValue = (node) => {
        if (!node) return Infinity;
        return Math.min(node.val, minValue(node.left), minValue(node.right));
    };

    const maxValue = (node) => {
        if (!node) return -Infinity;
        return Math.max(node.val, maxValue(node.left), maxValue(node.right));
    };

    const check = (node) => {
        if (!node) return true;

        const leftMax = maxValue(node.left);
        const rightMin = minValue(node.right);

        if (node.val <= leftMax || node.val >= rightMin) return false;

        return check(node.left) && check(node.right);
    };

    return check(root);
};
