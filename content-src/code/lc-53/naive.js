var maxSubArray = function(nums) {
    let answer = -Infinity;

    for (let i = 0; i < nums.length; i++) {
        let total = 0;

        for (let j = i; j < nums.length; j++) {
            total += nums[j];
            answer = Math.max(answer, total);
        }
    }

    return answer;
};
