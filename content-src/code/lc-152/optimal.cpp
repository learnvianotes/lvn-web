class Solution {
public:
    int maxProduct(vector<int>& nums) {
        long long currentMax = nums[0];
        long long currentMin = nums[0];
        long long answer = nums[0];

        for (int i = 1; i < (int)nums.size(); i++) {
            long long num = nums[i];

            if (num < 0) swap(currentMax, currentMin);

            currentMax = max(num, currentMax * num);
            currentMin = min(num, currentMin * num);

            answer = max(answer, currentMax);
        }

        return (int)answer;
    }
};
