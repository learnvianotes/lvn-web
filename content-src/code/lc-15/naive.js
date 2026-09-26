var threeSum = function(nums) {
    const result = new Map();
    const n = nums.length;
    for (let i = 0; i < n; i++)
        for (let j = i + 1; j < n; j++)
            for (let k = j + 1; k < n; k++)
                if (nums[i] + nums[j] + nums[k] === 0) {
                    const triplet = [nums[i], nums[j], nums[k]].sort((a, b) => a - b);
                    result.set(triplet.join(","), triplet);
                }
    return [...result.values()];
};
