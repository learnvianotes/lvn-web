class Solution {
public:
    int largestRectangleArea(vector<int>& heights) {
        stack<int> st;
        int answer = 0;
        heights.push_back(0);
        for (int i = 0; i < heights.size(); i++) {
            while (!st.empty() && heights[st.top()] > heights[i]) {
                int h = heights[st.top()];
                st.pop();
                int leftBoundary = st.empty() ? -1 : st.top();
                int width = i - leftBoundary - 1;
                answer = max(answer, h * width);
            }
            st.push(i);
        }
        heights.pop_back();
        return answer;
    }
};
