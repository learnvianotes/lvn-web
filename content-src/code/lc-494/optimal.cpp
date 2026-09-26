class Solution {
public:
    int findTargetSumWays(vector<int>& nums, int target) {
        memo.clear();
        return dfs(nums, target, 0, 0);
    }

private:
    map<pair<int, int>, int> memo;

    int dfs(vector<int>& nums, int target, int index, int total) {
        if (index == (int)nums.size()) return total == target ? 1 : 0;

        auto key = make_pair(index, total);
        auto it = memo.find(key);
        if (it != memo.end()) return it->second;

        int ways = dfs(nums, target, index + 1, total + nums[index])
                 + dfs(nums, target, index + 1, total - nums[index]);

        memo[key] = ways;
        return ways;
    }
};
