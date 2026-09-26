var isSameTree = function(p, q) {
    const queue = [[p, q]];
    let head = 0;

    while (head < queue.length) {
        const [a, b] = queue[head++];

        if (!a && !b) continue;

        if (!a || !b) return false;

        if (a.val !== b.val) return false;

        queue.push([a.left, b.left]);
        queue.push([a.right, b.right]);
    }

    return true;
};
