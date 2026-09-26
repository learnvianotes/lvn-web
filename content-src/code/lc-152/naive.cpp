class Solution {
public:
    int maxProduct(vector<int>& nums) {
        long long answer = nums[0];

        for (int i = 0; i < (int)nums.size(); i++) {
            long long product = 1;

            for (int j = i; j < (int)nums.size(); j++) {
                product *= nums[j];
                answer = max(answer, product);
            }
        }

        return (int)answer;
    }
};
