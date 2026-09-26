var goodNodes = function(root) {
    const dfs = (node, path) => {
        if (!node) return 0;

        path.push(node.val);

        let count = 0;
        if (node.val === path.reduce((a, b) => Math.max(a, b))) count++;

        count += dfs(node.left, path);
        count += dfs(node.right, path);

        path.pop();
        return count;
    };

    return dfs(root, []);
};
