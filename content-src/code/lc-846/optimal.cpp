class Solution {
public:
    bool isNStraightHand(vector<int>& hand, int groupSize) {
        if (hand.size() % groupSize != 0) {
            return false;
        }

        map<int, int> count;  // ordered by card value
        for (int card : hand) {
            count[card]++;
        }

        for (auto& [first, freq] : count) {
            if (freq == 0) {
                continue;
            }

            int frequency = freq;

            for (int value = first; value < first + groupSize; value++) {
                if (count[value] < frequency) {
                    return false;
                }

                count[value] -= frequency;
            }
        }

        return true;
    }
};
