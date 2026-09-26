var findMedianSortedArrays = function(nums1, nums2) {
    if (nums1.length > nums2.length) {
        [nums1, nums2] = [nums2, nums1];
    }

    const m = nums1.length;
    const n = nums2.length;

    let left = 0;
    let right = m;

    const half = Math.floor((m + n + 1) / 2);

    while (left <= right) {
        const partition1 = Math.floor((left + right) / 2);
        const partition2 = half - partition1;

        const left1 = partition1 > 0 ? nums1[partition1 - 1] : -Infinity;
        const right1 = partition1 < m ? nums1[partition1] : Infinity;
        const left2 = partition2 > 0 ? nums2[partition2 - 1] : -Infinity;
        const right2 = partition2 < n ? nums2[partition2] : Infinity;

        // Correct partition
        if (left1 <= right2 && left2 <= right1) {
            if ((m + n) % 2) {
                return Math.max(left1, left2);
            }

            return (Math.max(left1, left2) + Math.min(right1, right2)) / 2;
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
};
