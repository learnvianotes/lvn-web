var maxArea = function(height) {
    let answer = 0;
    for (let i = 0; i < height.length; i++)
        for (let j = i + 1; j < height.length; j++) {
            const width = j - i;
            const area = width * Math.min(height[i], height[j]);
            answer = Math.max(answer, area);
        }
    return answer;
};
