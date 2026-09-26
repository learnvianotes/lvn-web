class Solution {
public:
    int minEatingSpeed(vector<int>& piles, int h) {
        int left = 1;
        int right = *max_element(piles.begin(), piles.end());

        int answer = right;

        while (left <= right) {
            int speed = left + (right - left) / 2;

            long long hours = 0;

            for (int pile : piles) {
                hours += ((long long) pile + speed - 1) / speed;
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
};
