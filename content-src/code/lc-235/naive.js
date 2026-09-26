var lowestCommonAncestor = function(root, p, q) {
    const pathTo = (node, target) => {
        const path = [];

        while (node) {
            path.push(node);

            if (target.val < node.val) node = node.left;
            else if (target.val > node.val) node = node.right;
            else break;
        }

        return path;
    };

    const pPath = pathTo(root, p);
    const qPath = pathTo(root, q);

    let answer = root;

    for (let i = 0; i < Math.min(pPath.length, qPath.length); i++) {
        if (pPath[i] !== qPath[i]) break;
        answer = pPath[i];
    }

    return answer;
};
