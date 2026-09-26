var maxPathSum = function(root) {
    let answer = -Infinity;

    const dfs = (node) => {
        if (!node) return 0;

        const left = Math.max(0, dfs(node.left));
        const right = Math.max(0, dfs(node.right));

        const current = node.val + left + right;

        answer = Math.max(answer, current);

        return node.val + Math.max(left, right);
    };

    dfs(root);
    return answer;
};
