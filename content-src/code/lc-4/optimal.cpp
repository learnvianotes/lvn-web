class Solution {
public:
    double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {
        if (nums1.size() > nums2.size()) {
            return findMedianSortedArrays(nums2, nums1);
        }

        int m = nums1.size();
        int n = nums2.size();

        int left = 0;
        int right = m;

        int half = (m + n + 1) / 2;

        while (left <= right) {
            int partition1 = (left + right) / 2;
            int partition2 = half - partition1;

            int left1 = partition1 > 0 ? nums1[partition1 - 1] : INT_MIN;
            int right1 = partition1 < m ? nums1[partition1] : INT_MAX;
            int left2 = partition2 > 0 ? nums2[partition2 - 1] : INT_MIN;
            int right2 = partition2 < n ? nums2[partition2] : INT_MAX;

            // Correct partition
            if (left1 <= right2 && left2 <= right1) {
                if ((m + n) % 2) {
                    return max(left1, left2);
                }

                return ((double) max(left1, left2) + min(right1, right2)) / 2;
            }
            // Partition1 is too far right
            else if (left1 > right2) {
                right = partition1 - 1;
            }
            // Partition1 is too far left
            else {
                left = partition1 + 1;
            }
        }

        return 0;
    }
};
