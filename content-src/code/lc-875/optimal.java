class Solution {
    public int minEatingSpeed(int[] piles, int h) {
        int left = 1;
        int right = 0;
        for (int pile : piles) {
            right = Math.max(right, pile);
        }

        int answer = right;

        while (left <= right) {
            int speed = left + (right - left) / 2;

            long hours = 0;

            for (int pile : piles) {
                hours += ((long) pile + speed - 1) / speed;
            }

            if (hours <= h) {
                answer = speed;
                right = speed - 1;
            } else {
                left = speed + 1;
            }
        }

        return answer;
    }
}
