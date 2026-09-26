var subsets = function(nums) {
    const result = [];

    const backtrack = (index, current) => {
        if (index === nums.length) {
            result.push([...current]);
            return;
        }

        // Don't take nums[index]
        backtrack(index + 1, current);

        // Take nums[index]
        current.push(nums[index]);
        backtrack(index + 1, current);
        current.pop();
    };

    backtrack(0, []);
    return result;
};
