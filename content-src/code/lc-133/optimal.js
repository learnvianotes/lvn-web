var cloneGraph = function(node) {
    if (!node) return null;

    const clones = new Map([[node, new _Node(node.val)]]);

    const queue = [node];
    let head = 0;

    while (head < queue.length) {
        const current = queue[head++];

        for (const neighbor of current.neighbors) {
            if (!clones.has(neighbor)) {
                clones.set(neighbor, new _Node(neighbor.val));
                queue.push(neighbor);
            }

            clones.get(current).neighbors.push(clones.get(neighbor));
        }
    }

    return clones.get(node);
};
