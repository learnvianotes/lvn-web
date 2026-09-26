var subsetsWithDup = function(nums) {
    nums.sort((a, b) => a - b);
    const result = new Map();  // key -> subset, acts as a set of subsets

    const backtrack = (index, current) => {
        if (index === nums.length) {
            result.set(current.join(','), [...current]);
            return;
        }

        // Don't take
        backtrack(index + 1, current);

        // Take
        current.push(nums[index]);
        backtrack(index + 1, current);
        current.pop();
    };

    backtrack(0, []);
    return [...result.values()];
};
