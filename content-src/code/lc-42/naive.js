var trap = function(height) {
    let water = 0;
    const n = height.length;
    for (let i = 0; i < n; i++) {
        const leftMax = Math.max(...height.slice(0, i + 1));
        const rightMax = Math.max(...height.slice(i));
        water += Math.min(leftMax, rightMax) - height[i];
    }
    return water;
};
