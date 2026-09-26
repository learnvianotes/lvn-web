class Solution {
    public boolean isNStraightHand(int[] hand, int groupSize) {
        if (hand.length % groupSize != 0) {
            return false;
        }

        Arrays.sort(hand);
        List<Integer> cards = new ArrayList<>();
        for (int card : hand) {
            cards.add(card);
        }

        while (!cards.isEmpty()) {
            int first = cards.get(0);

            for (int value = first; value < first + groupSize; value++) {
                if (!cards.contains(value)) {
                    return false;
                }

                cards.remove(Integer.valueOf(value));
            }
        }

        return true;
    }
}
