var invertTree = function(root) {
    if (!root) return null;

    const queue = [root];
    let head = 0;

    while (head < queue.length) {
        const node = queue[head++];

        [node.left, node.right] = [node.right, node.left];

        if (node.left) queue.push(node.left);
        if (node.right) queue.push(node.right);
    }

    return root;
};
