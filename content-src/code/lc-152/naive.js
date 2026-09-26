var maxProduct = function(nums) {
    let answer = nums[0];

    for (let i = 0; i < nums.length; i++) {
        let product = 1;

        for (let j = i; j < nums.length; j++) {
            product *= nums[j];
            answer = Math.max(answer, product);
        }
    }

    return answer;
};
