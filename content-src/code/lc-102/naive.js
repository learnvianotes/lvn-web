var levelOrder = function(root) {
    const result = [];

    const dfs = (node, level) => {
        if (!node) return;

        if (level === result.length) result.push([]);

        result[level].push(node.val);

        dfs(node.left, level + 1);
        dfs(node.right, level + 1);
    };

    dfs(root, 0);
    return result;
};
