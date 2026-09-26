var jump = function(nums) {
    const n = nums.length;
    let answer = Infinity;

    const dfs = (index, jumps) => {
        if (index >= n - 1) {
            answer = Math.min(answer, jumps);
            return;
        }

        if (jumps >= answer) {
            return;
        }

        for (let jump = 1; jump <= nums[index]; jump++) {
            dfs(index + jump, jumps + 1);
        }
    };

    dfs(0, 0);

    return answer;
};
