class Solution {
    public List<Integer> partitionLabels(String s) {
        List<Integer> result = new ArrayList<>();
        int n = s.length();
        int start = 0;

        while (start < n) {
            Set<Character> chars = new HashSet<>();
            int end = start;

            while (end < n) {
                chars.add(s.charAt(end));

                int last = 0;
                for (int i = 0; i < n; i++) {
                    if (chars.contains(s.charAt(i))) {
                        last = i;
                    }
                }

                if (last == end) {
                    break;
                }

                end++;
            }

            result.add(end - start + 1);
            start = end + 1;
        }

        return result;
    }
}
