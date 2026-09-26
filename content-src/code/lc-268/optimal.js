var missingNumber = function(nums) {
    const n = nums.length;
    let answer = n;

    for (let i = 0; i < n; i++) {
        answer ^= i;
        answer ^= nums[i];
    }

    return answer;
};
