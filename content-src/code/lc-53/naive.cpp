class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        int answer = INT_MIN;

        for (int i = 0; i < (int)nums.size(); i++) {
            int total = 0;

            for (int j = i; j < (int)nums.size(); j++) {
                total += nums[j];
                answer = max(answer, total);
            }
        }

        return answer;
    }
};
