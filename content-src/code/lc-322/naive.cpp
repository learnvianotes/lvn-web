class Solution {
public:
    int coinChange(vector<int>& coins, int amount) {
        int result = dfs(coins, amount);
        return result == INT_MAX ? -1 : result;
    }

private:
    int dfs(vector<int>& coins, int remaining) {
        if (remaining == 0) return 0;
        if (remaining < 0) return INT_MAX;

        int answer = INT_MAX;

        for (int coin : coins) {
            int sub = dfs(coins, remaining - coin);
            if (sub != INT_MAX) {
                answer = min(answer, 1 + sub);
            }
        }

        return answer;
    }
};
