class Solution {
public:
    int minEatingSpeed(vector<int>& piles, int h) {
        int maxPile = *max_element(piles.begin(), piles.end());

        for (int speed = 1; speed <= maxPile; speed++) {
            long long hours = 0;

            for (int pile : piles) {
                hours += ((long long) pile + speed - 1) / speed;
            }

            if (hours <= h) {
                return speed;
            }
        }

        return maxPile;
    }
};
