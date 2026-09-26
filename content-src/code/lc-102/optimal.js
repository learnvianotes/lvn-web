var levelOrder = function(root) {
    if (!root) return [];

    const result = [];
    let queue = [root];

    while (queue.length) {
        const level = [];
        const next = [];

        for (const node of queue) {
            level.push(node.val);

            if (node.left) next.push(node.left);
            if (node.right) next.push(node.right);
        }

        result.push(level);
        queue = next;
    }

    return result;
};
