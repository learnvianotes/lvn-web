class Solution {
    public int[] countBits(int n) {
        int[] result = new int[n + 1];

        for (int num = 1; num <= n; num++) {
            result[num] = result[num >> 1] + (num & 1);
        }

        return result;
    }
}
