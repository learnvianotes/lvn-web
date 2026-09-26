var reverseBits = function(n) {
    let binary = "";

    for (let i = 0; i < 32; i++) {
        binary += String(n & 1);
        n >>>= 1;
    }

    let result = 0;

    for (const bit of binary) {
        result = (result << 1) | Number(bit);
    }

    return result >>> 0;  // reinterpret as unsigned
};
