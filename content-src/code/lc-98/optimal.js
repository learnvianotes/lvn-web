var isValidBST = function(root) {
    const dfs = (node, low, high) => {
        if (!node) return true;

        if (!(low < node.val && node.val < high)) return false;

        return dfs(node.left, low, node.val) && dfs(node.right, node.val, high);
    };

    return dfs(root, -Infinity, Infinity);
};
