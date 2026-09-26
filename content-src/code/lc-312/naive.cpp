class Solution {
public:
    int maxCoins(vector<int>& nums) {
        return dfs(nums);
    }

private:
    int dfs(vector<int> nums) {
        if (nums.empty()) return 0;

        int n = nums.size();
        int answer = 0;

        for (int i = 0; i < n; i++) {
            int left = i > 0 ? nums[i - 1] : 1;
            int right = i + 1 < n ? nums[i + 1] : 1;

            int coins = left * nums[i] * right;

            vector<int> remaining(nums.begin(), nums.begin() + i);
            remaining.insert(remaining.end(), nums.begin() + i + 1, nums.end());

            answer = max(answer, coins + dfs(remaining));
        }

        return answer;
    }
};
