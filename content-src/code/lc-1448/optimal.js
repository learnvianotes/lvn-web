var goodNodes = function(root) {
    const dfs = (node, maxSoFar) => {
        if (!node) return 0;

        const good = node.val >= maxSoFar ? 1 : 0;

        maxSoFar = Math.max(maxSoFar, node.val);

        return good + dfs(node.left, maxSoFar) + dfs(node.right, maxSoFar);
    };

    return dfs(root, root.val);
};
