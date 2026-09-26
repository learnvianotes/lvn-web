class Solution {
public:
    bool canJump(vector<int>& nums) {
        return dfs(nums, 0);
    }

private:
    bool dfs(vector<int>& nums, int index) {
        int n = nums.size();
        if (index >= n - 1) {
            return true;
        }

        int maxJump = nums[index];

        for (int jump = 1; jump <= maxJump; jump++) {
            if (dfs(nums, index + jump)) {
                return true;
            }
        }

        return false;
    }
};
