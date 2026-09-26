var multiply = function(num1, num2) {
    if (num1 === "0" || num2 === "0") {
        return "0";
    }

    const n = num1.length;
    const m = num2.length;
    const result = new Array(n + m).fill(0);

    for (let i = n - 1; i >= 0; i--) {
        for (let j = m - 1; j >= 0; j--) {
            const product = Number(num1[i]) * Number(num2[j]);
            const pos = i + j + 1;

            result[pos] += product;
            result[pos - 1] += Math.floor(result[pos] / 10);
            result[pos] %= 10;
        }
    }

    // Strip leading zeros
    let start = 0;
    while (start < result.length - 1 && result[start] === 0) {
        start++;
    }

    return result.slice(start).join("");
};
