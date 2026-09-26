class Solution {
    public int maxCoins(int[] nums) {
        List<Integer> list = new ArrayList<>();
        for (int num : nums) list.add(num);
        return dfs(list);
    }

    private int dfs(List<Integer> nums) {
        if (nums.isEmpty()) return 0;

        int n = nums.size();
        int answer = 0;

        for (int i = 0; i < n; i++) {
            int left = i > 0 ? nums.get(i - 1) : 1;
            int right = i + 1 < n ? nums.get(i + 1) : 1;

            int coins = left * nums.get(i) * right;

            List<Integer> remaining = new ArrayList<>(nums.subList(0, i));
            remaining.addAll(nums.subList(i + 1, n));

            answer = Math.max(answer, coins + dfs(remaining));
        }

        return answer;
    }
}
