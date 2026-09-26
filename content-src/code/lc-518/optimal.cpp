class Solution {
public:
    int change(int amount, vector<int>& coins) {
        // unsigned: unrelated cells may overflow, but dp[amount] always fits
        vector<unsigned long long> dp(amount + 1, 0);
        dp[0] = 1;

        for (int coin : coins) {
            for (int current = coin; current <= amount; current++) {
                dp[current] += dp[current - coin];
            }
        }

        return (int)dp[amount];
    }
};
