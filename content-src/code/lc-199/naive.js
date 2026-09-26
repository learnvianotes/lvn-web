var rightSideView = function(root) {
    const result = [];

    const dfs = (node, depth) => {
        if (!node) return;

        if (depth === result.length) result.push(node.val);

        dfs(node.right, depth + 1);
        dfs(node.left, depth + 1);
    };

    dfs(root, 0);
    return result;
};
