class Solution {
    public boolean isHappy(int n) {
        int slow = n;
        int fast = nextNumber(n);

        while (fast != 1 && slow != fast) {
            slow = nextNumber(slow);
            fast = nextNumber(nextNumber(fast));
        }

        return fast == 1;
    }

    private int nextNumber(int num) {
        int total = 0;

        while (num > 0) {
            int digit = num % 10;
            total += digit * digit;
            num /= 10;
        }

        return total;
    }
}
