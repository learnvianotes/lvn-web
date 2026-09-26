class Solution {
public:
    int findMin(vector<int>& nums) {
        int answer = nums[0];

        for (int num : nums) {
            answer = min(answer, num);
        }

        return answer;
    }
};
