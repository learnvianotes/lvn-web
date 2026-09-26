var findMin = function(nums) {
    let answer = nums[0];

    for (const num of nums) {
        answer = Math.min(answer, num);
    }

    return answer;
};
