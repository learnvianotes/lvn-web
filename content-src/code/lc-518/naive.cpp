class Solution {
public:
    int change(int amount, vector<int>& coins) {
        return dfs(coins, 0, amount);
    }

private:
    int dfs(vector<int>& coins, int index, int remaining) {
        if (remaining == 0) return 1;
        if (index == (int)coins.size() || remaining < 0) return 0;

        // Use current coin
        int use = dfs(coins, index, remaining - coins[index]);

        // Skip current coin
        int skip = dfs(coins, index + 1, remaining);

        return use + skip;
    }
};
