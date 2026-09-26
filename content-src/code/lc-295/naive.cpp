class MedianFinder {
    vector<int> nums;

public:
    MedianFinder() {}

    void addNum(int num) {
        nums.push_back(num);
    }

    double findMedian() {
        sort(nums.begin(), nums.end());

        int n = nums.size();

        if (n % 2) return nums[n / 2];

        return (nums[n / 2 - 1] + nums[n / 2]) / 2.0;
    }
};
