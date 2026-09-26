var maxSlidingWindow = function(nums, k) {
    const result = [];
    const dq = [];
    let head = 0; // dq[head..] is the live deque
    for (let right = 0; right < nums.length; right++) {
        // Remove smaller values
        while (dq.length > head && nums[dq[dq.length - 1]] <= nums[right]) dq.pop();
        dq.push(right);
        // Remove indices outside window
        const left = right - k + 1;
        if (dq[head] < left) head++;
        if (right >= k - 1) result.push(nums[dq[head]]);
    }
    return result;
};
