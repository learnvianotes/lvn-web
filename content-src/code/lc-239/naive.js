var maxSlidingWindow = function(nums, k) {
    const result = [];
    for (let i = 0; i + k <= nums.length; i++)
        result.push(Math.max(...nums.slice(i, i + k)));
    return result;
};
