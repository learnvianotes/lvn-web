var getSum = function(a, b) {
    // JS bitwise operators work on 32-bit signed ints, so no MASK is needed
    while (b !== 0) {
        const carry = (a & b) << 1;
        a = a ^ b;
        b = carry;
    }

    return a;
};
