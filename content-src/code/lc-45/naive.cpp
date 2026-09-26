class Solution {
public:
    int jump(vector<int>& nums) {
        answer = INT_MAX;
        dfs(nums, 0, 0);
        return answer;
    }

private:
    int answer;

    void dfs(vector<int>& nums, int index, int jumps) {
        int n = nums.size();

        if (index >= n - 1) {
            answer = min(answer, jumps);
            return;
        }

        if (jumps >= answer) {
            return;
        }

        for (int jump = 1; jump <= nums[index]; jump++) {
            dfs(nums, index + jump, jumps + 1);
        }
    }
};
