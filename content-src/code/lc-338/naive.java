class Solution {
    public int[] countBits(int n) {
        int[] result = new int[n + 1];

        for (int num = 0; num <= n; num++) {
            int count = 0;
            int x = num;

            while (x != 0) {
                x &= x - 1;
                count++;
            }

            result[num] = count;
        }

        return result;
    }
}
