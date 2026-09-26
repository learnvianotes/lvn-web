var isSubtree = function(root, subRoot) {
    const serialize = (node) => {
        if (!node) return "#";

        return "," + node.val + serialize(node.left) + serialize(node.right);
    };

    const text = serialize(root);
    const pattern = serialize(subRoot);

    // KMP algorithm
    const lps = new Array(pattern.length).fill(0);

    let j = 0;
    for (let i = 1; i < pattern.length; i++) {
        while (j > 0 && pattern[i] !== pattern[j]) j = lps[j - 1];

        if (pattern[i] === pattern[j]) j++;

        lps[i] = j;
    }

    j = 0;

    for (let i = 0; i < text.length; i++) {
        while (j > 0 && text[i] !== pattern[j]) j = lps[j - 1];

        if (text[i] === pattern[j]) j++;

        if (j === pattern.length) return true;
    }

    return false;
};
