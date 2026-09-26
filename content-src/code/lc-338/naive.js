var countBits = function(n) {
    const result = [];

    for (let num = 0; num <= n; num++) {
        let count = 0;
        let x = num;

        while (x) {
            x &= x - 1;
            count++;
        }

        result.push(count);
    }

    return result;
};
