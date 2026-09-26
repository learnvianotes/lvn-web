var missingNumber = function(nums) {
    const n = nums.length;
    const values = new Set(nums);

    for (let num = 0; num <= n; num++) {
        if (!values.has(num)) {
            return num;
        }
    }

    return -1;
};
