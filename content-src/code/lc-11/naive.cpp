class Solution {
public:
    int maxArea(vector<int>& height) {
        int answer = 0;
        for (int i = 0; i < height.size(); i++)
            for (int j = i + 1; j < height.size(); j++) {
                int width = j - i;
                int area = width * min(height[i], height[j]);
                answer = max(answer, area);
            }
        return answer;
    }
};
