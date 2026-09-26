class Solution {
    public int maxArea(int[] height) {
        int answer = 0;
        for (int i = 0; i < height.length; i++)
            for (int j = i + 1; j < height.length; j++) {
                int width = j - i;
                int area = width * Math.min(height[i], height[j]);
                answer = Math.max(answer, area);
            }
        return answer;
    }
}
