class Solution {
    private String[] words;
    private String chars;
    private int[] rank = new int[26];

    public String alienOrder(String[] words) {
        this.words = words;

        StringBuilder sb = new StringBuilder();
        for (String word : words)
            for (char c : word.toCharArray())
                if (sb.indexOf(String.valueOf(c)) == -1) sb.append(c);
        chars = sb.toString();

        // Try every ordering of the letters
        String result = permute(new StringBuilder(), new boolean[chars.length()]);
        return result == null ? "" : result;
    }

    private String permute(StringBuilder order, boolean[] used) {
        if (order.length() == chars.length())
            return isSorted(order) ? order.toString() : null;

        for (int i = 0; i < chars.length(); i++) {
            if (used[i]) continue;

            used[i] = true;
            order.append(chars.charAt(i));

            String result = permute(order, used);
            if (result != null) return result;

            order.deleteCharAt(order.length() - 1);
            used[i] = false;
        }

        return null;
    }

    // Are the words sorted under this alphabet order?
    private boolean isSorted(StringBuilder order) {
        for (int i = 0; i < order.length(); i++) rank[order.charAt(i) - 'a'] = i;

        for (int i = 0; i + 1 < words.length; i++) {
            String w1 = words[i], w2 = words[i + 1];
            int j = 0;

            while (j < w1.length() && j < w2.length() && w1.charAt(j) == w2.charAt(j)) j++;

            if (j == w1.length() || j == w2.length()) {
                if (w1.length() > w2.length()) return false;  // longer word before its prefix
            } else if (rank[w1.charAt(j) - 'a'] > rank[w2.charAt(j) - 'a']) {
                return false;
            }
        }

        return true;
    }
}
