class Solution {
public:
    int missingNumber(vector<int>& nums) {
        int n = nums.size();
        int answer = n;

        for (int i = 0; i < n; i++) {
            answer ^= i;
            answer ^= nums[i];
        }

        return answer;
    }
};
