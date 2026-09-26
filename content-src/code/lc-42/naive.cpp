class Solution {
public:
    int trap(vector<int>& height) {
        int water = 0;
        int n = height.size();
        for (int i = 0; i < n; i++) {
            int leftMax = *max_element(height.begin(), height.begin() + i + 1);
            int rightMax = *max_element(height.begin() + i, height.end());
            water += min(leftMax, rightMax) - height[i];
        }
        return water;
    }
};
