var maxDepth = function(root) {
    if (!root) return 0;

    let queue = [root];
    let depth = 0;

    while (queue.length) {
        const next = [];

        for (const node of queue) {
            if (node.left) next.push(node.left);
            if (node.right) next.push(node.right);
        }

        queue = next;
        depth++;
    }

    return depth;
};
