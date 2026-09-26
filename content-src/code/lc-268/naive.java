class Solution {
    public int missingNumber(int[] nums) {
        int n = nums.length;
        Set<Integer> values = new HashSet<>();
        for (int num : nums) {
            values.add(num);
        }

        for (int num = 0; num <= n; num++) {
            if (!values.contains(num)) {
                return num;
            }
        }

        return -1;
    }
}
