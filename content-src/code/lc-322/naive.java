class Solution {
    public int coinChange(int[] coins, int amount) {
        int result = dfs(coins, amount);
        return result == Integer.MAX_VALUE ? -1 : result;
    }

    private int dfs(int[] coins, int remaining) {
        if (remaining == 0) return 0;
        if (remaining < 0) return Integer.MAX_VALUE;

        int answer = Integer.MAX_VALUE;

        for (int coin : coins) {
            int sub = dfs(coins, remaining - coin);
            if (sub != Integer.MAX_VALUE) {
                answer = Math.min(answer, 1 + sub);
            }
        }

        return answer;
    }
}
