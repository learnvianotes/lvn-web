class Solution {
public:
    int missingNumber(vector<int>& nums) {
        int n = nums.size();
        unordered_set<int> values(nums.begin(), nums.end());

        for (int num = 0; num <= n; num++) {
            if (!values.count(num)) {
                return num;
            }
        }

        return -1;
    }
};
