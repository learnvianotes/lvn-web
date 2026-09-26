var maxArea = function(height) {
    let left = 0, right = height.length - 1;
    let answer = 0;
    while (left < right) {
        const width = right - left;
        const area = width * Math.min(height[left], height[right]);
        answer = Math.max(answer, area);
        if (height[left] < height[right]) left++;
        else right--;
    }
    return answer;
};
