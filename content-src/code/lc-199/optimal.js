var rightSideView = function(root) {
    if (!root) return [];

    const result = [];
    let queue = [root];

    while (queue.length) {
        const size = queue.length;
        const next = [];

        for (let i = 0; i < size; i++) {
            const node = queue[i];

            if (node.left) next.push(node.left);
            if (node.right) next.push(node.right);

            if (i === size - 1) result.push(node.val);
        }

        queue = next;
    }

    return result;
};
