class Solution {
    public int largestRectangleArea(int[] heights) {
        Deque<Integer> stack = new ArrayDeque<>();
        int answer = 0;
        int n = heights.length;
        for (int i = 0; i <= n; i++) {
            int height = i == n ? 0 : heights[i]; // sentinel 0 at the end
            while (!stack.isEmpty() && heights[stack.peek()] > height) {
                int h = heights[stack.pop()];
                int leftBoundary = stack.isEmpty() ? -1 : stack.peek();
                int width = i - leftBoundary - 1;
                answer = Math.max(answer, h * width);
            }
            stack.push(i);
        }
        return answer;
    }
}
