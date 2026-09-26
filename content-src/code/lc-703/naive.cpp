class KthLargest {
    int k;
    vector<int> nums;

public:
    KthLargest(int k, vector<int>& nums) : k(k), nums(nums) {}

    int add(int val) {
        nums.push_back(val);
        sort(nums.begin(), nums.end(), greater<int>());

        return nums[k - 1];
    }
};
