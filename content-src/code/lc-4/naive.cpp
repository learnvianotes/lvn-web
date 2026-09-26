class Solution {
public:
    double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {
        vector<int> merged;

        int i = 0;
        int j = 0;

        while (i < nums1.size() && j < nums2.size()) {
            if (nums1[i] <= nums2[j]) {
                merged.push_back(nums1[i++]);
            } else {
                merged.push_back(nums2[j++]);
            }
        }

        merged.insert(merged.end(), nums1.begin() + i, nums1.end());
        merged.insert(merged.end(), nums2.begin() + j, nums2.end());

        int n = merged.size();

        if (n % 2) {
            return merged[n / 2];
        }

        return (merged[n / 2 - 1] + (double) merged[n / 2]) / 2;
    }
};
