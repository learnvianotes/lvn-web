var partitionLabels = function(s) {
    const result = [];
    const n = s.length;
    let start = 0;

    while (start < n) {
        const chars = new Set();
        let end = start;

        while (end < n) {
            chars.add(s[end]);

            let last = 0;
            for (let i = 0; i < n; i++) {
                if (chars.has(s[i])) {
                    last = i;
                }
            }

            if (last === end) {
                break;
            }

            end++;
        }

        result.push(end - start + 1);
        start = end + 1;
    }

    return result;
};
