class Solution {
    public int minEatingSpeed(int[] piles, int h) {
        int maxPile = 0;
        for (int pile : piles) {
            maxPile = Math.max(maxPile, pile);
        }

        for (int speed = 1; speed <= maxPile; speed++) {
            long hours = 0;

            for (int pile : piles) {
                hours += ((long) pile + speed - 1) / speed;
            }

            if (hours <= h) {
                return speed;
            }
        }

        return maxPile;
    }
}
