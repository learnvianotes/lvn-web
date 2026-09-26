var isSubtree = function(root, subRoot) {
    const same = (a, b) => {
        if (!a && !b) return true;
        if (!a || !b) return false;

        return a.val === b.val && same(a.left, b.left) && same(a.right, b.right);
    };

    if (!root) return false;

    if (same(root, subRoot)) return true;

    return isSubtree(root.left, subRoot) || isSubtree(root.right, subRoot);
};
