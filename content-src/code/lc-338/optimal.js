var countBits = function(n) {
    const result = new Array(n + 1).fill(0);

    for (let num = 1; num <= n; num++) {
        result[num] = result[num >> 1] + (num & 1);
    }

    return result;
};
