var largestRectangleArea = function(heights) {
    let answer = 0;
    const n = heights.length;
    for (let i = 0; i < n; i++) {
        let left = i, right = i;
        while (left - 1 >= 0 && heights[left - 1] >= heights[i]) left--;
        while (right + 1 < n && heights[right + 1] >= heights[i]) right++;
        const width = right - left + 1;
        answer = Math.max(answer, heights[i] * width);
    }
    return answer;
};
