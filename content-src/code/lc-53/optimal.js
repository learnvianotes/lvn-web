var maxSubArray = function(nums) {
    let current = nums[0];
    let answer = nums[0];

    for (let i = 1; i < nums.length; i++) {
        current = Math.max(nums[i], current + nums[i]);
        answer = Math.max(answer, current);
    }

    return answer;
};
