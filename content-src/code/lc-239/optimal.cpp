class Solution {
public:
    vector<int> maxSlidingWindow(vector<int>& nums, int k) {
        vector<int> result;
        deque<int> dq;
        for (int right = 0; right < nums.size(); right++) {
            // Remove smaller values
            while (!dq.empty() && nums[dq.back()] <= nums[right]) dq.pop_back();
            dq.push_back(right);
            // Remove indices outside window
            int left = right - k + 1;
            if (dq.front() < left) dq.pop_front();
            if (right >= k - 1) result.push_back(nums[dq.front()]);
        }
        return result;
    }
};
