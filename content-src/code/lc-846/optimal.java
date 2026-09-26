class Solution {
    public boolean isNStraightHand(int[] hand, int groupSize) {
        if (hand.length % groupSize != 0) {
            return false;
        }

        TreeMap<Integer, Integer> count = new TreeMap<>();
        for (int card : hand) {
            count.merge(card, 1, Integer::sum);
        }

        for (int first : new ArrayList<>(count.keySet())) {
            if (count.get(first) == 0) {
                continue;
            }

            int frequency = count.get(first);

            for (int value = first; value < first + groupSize; value++) {
                if (count.getOrDefault(value, 0) < frequency) {
                    return false;
                }

                count.put(value, count.get(value) - frequency);
            }
        }

        return true;
    }
}
