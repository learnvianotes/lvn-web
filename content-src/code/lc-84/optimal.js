var largestRectangleArea = function(heights) {
    const stack = [];
    let answer = 0;
    heights.push(0);
    for (let i = 0; i < heights.length; i++) {
        while (stack.length && heights[stack[stack.length - 1]] > heights[i]) {
            const h = heights[stack.pop()];
            const leftBoundary = stack.length ? stack[stack.length - 1] : -1;
            const width = i - leftBoundary - 1;
            answer = Math.max(answer, h * width);
        }
        stack.push(i);
    }
    heights.pop();
    return answer;
};
