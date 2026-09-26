var alienOrder = function(words) {
    const chars = [...new Set(words.join(""))];

    // Are the words sorted under this alphabet order?
    const isSorted = (order) => {
        const rank = {};
        order.forEach((c, i) => rank[c] = i);

        for (let i = 0; i + 1 < words.length; i++) {
            const w1 = words[i], w2 = words[i + 1];
            let j = 0;

            while (j < w1.length && j < w2.length && w1[j] === w2[j]) j++;

            if (j === w1.length || j === w2.length) {
                if (w1.length > w2.length) return false;  // longer word before its prefix
            } else if (rank[w1[j]] > rank[w2[j]]) {
                return false;
            }
        }

        return true;
    };

    // Try every ordering of the letters
    const used = new Array(chars.length).fill(false);
    const order = [];

    const permute = () => {
        if (order.length === chars.length) return isSorted(order);

        for (let i = 0; i < chars.length; i++) {
            if (used[i]) continue;

            used[i] = true;
            order.push(chars[i]);

            if (permute()) return true;

            order.pop();
            used[i] = false;
        }

        return false;
    };

    return permute() ? order.join("") : "";
};
