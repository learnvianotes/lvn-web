var reverse = function(x) {
    const sign = x < 0 ? -1 : 1;
    x = Math.abs(x);

    let reversedNum = parseInt(String(x).split("").reverse().join(""), 10);
    reversedNum *= sign;

    if (reversedNum < -(2 ** 31) || reversedNum > 2 ** 31 - 1) {
        return 0;
    }

    return reversedNum;
};
