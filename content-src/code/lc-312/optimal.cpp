class Solution {
public:
    int maxCoins(vector<int>& input) {
        vector<int> nums = {1};
        nums.insert(nums.end(), input.begin(), input.end());
        nums.push_back(1);

        int n = nums.size();
        vector<vector<int>> dp(n, vector<int>(n, 0));

        for (int length = 2; length < n; length++) {
            for (int left = 0; left < n - length; left++) {
                int right = left + length;

                for (int k = left + 1; k < right; k++) {
                    int coins = nums[left] * nums[k] * nums[right];

                    dp[left][right] = max(dp[left][right],
                                          dp[left][k] + coins + dp[k][right]);
                }
            }
        }

        return dp[0][n - 1];
    }
};
