var isHappy = function(n) {
    const nextNumber = (num) => {
        let total = 0;

        while (num > 0) {
            const digit = num % 10;
            total += digit * digit;
            num = Math.floor(num / 10);
        }

        return total;
    };

    let slow = n;
    let fast = nextNumber(n);

    while (fast !== 1 && slow !== fast) {
        slow = nextNumber(slow);
        fast = nextNumber(nextNumber(fast));
    }

    return fast === 1;
};
