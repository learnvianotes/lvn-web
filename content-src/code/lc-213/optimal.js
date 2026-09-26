var rob = function(nums) {
    if (nums.length === 1) return nums[0];

    const robLinear = (arr) => {
        let prev2 = 0, prev1 = 0;

        for (const money of arr) {
            const current = Math.max(prev1, money + prev2);
            prev2 = prev1;
            prev1 = current;
        }

        return prev1;
    };

    return Math.max(robLinear(nums.slice(0, -1)), robLinear(nums.slice(1)));
};
