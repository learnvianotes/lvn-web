class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        if (!wordList.contains(endWord)) return 0;

        Map<String, List<String>> patterns = new HashMap<>();

        for (String word : wordList) {
            for (int i = 0; i < word.length(); i++) {
                String pattern = word.substring(0, i) + "*" + word.substring(i + 1);
                patterns.computeIfAbsent(pattern, key -> new ArrayList<>()).add(word);
            }
        }

        Set<String> visited = new HashSet<>();
        visited.add(beginWord);

        Deque<String> queue = new ArrayDeque<>();
        queue.offer(beginWord);
        int distance = 1;

        while (!queue.isEmpty()) {
            for (int size = queue.size(); size > 0; size--) {
                String word = queue.poll();

                if (word.equals(endWord)) return distance;

                for (int i = 0; i < word.length(); i++) {
                    String pattern = word.substring(0, i) + "*" + word.substring(i + 1);
                    List<String> neighbors = patterns.getOrDefault(pattern, Collections.emptyList());

                    for (String neighbor : neighbors) {
                        if (visited.add(neighbor)) queue.offer(neighbor);
                    }

                    patterns.remove(pattern);
                }
            }

            distance++;
        }

        return 0;
    }
}
