var plusOne = function(digits) {
    let number = 0n;

    for (const digit of digits) {
        number = number * 10n + BigInt(digit);
    }

    number += 1n;

    return [...number.toString()].map(Number);
};
