class Solution {
public:
    bool isNStraightHand(vector<int>& hand, int groupSize) {
        if (hand.size() % groupSize != 0) {
            return false;
        }

        sort(hand.begin(), hand.end());

        while (!hand.empty()) {
            int first = hand[0];

            for (int value = first; value < first + groupSize; value++) {
                auto it = find(hand.begin(), hand.end(), value);
                if (it == hand.end()) {
                    return false;
                }

                hand.erase(it);
            }
        }

        return true;
    }
};
