class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        if (!wordList.contains(endWord)) return 0;

        List<String> words = new ArrayList<>(wordList);
        words.add(beginWord);
        int n = words.size();

        // Compare every pair of words to build the graph
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) graph.add(new ArrayList<>());

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (oneApart(words.get(i), words.get(j))) {
                    graph.get(i).add(j);
                    graph.get(j).add(i);
                }
            }
        }

        boolean[] visited = new boolean[n];
        Deque<int[]> queue = new ArrayDeque<>();
        queue.offer(new int[]{n - 1, 1});
        visited[n - 1] = true;

        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            int i = cur[0], distance = cur[1];

            if (words.get(i).equals(endWord)) return distance;

            for (int j : graph.get(i)) {
                if (!visited[j]) {
                    visited[j] = true;
                    queue.offer(new int[]{j, distance + 1});
                }
            }
        }

        return 0;
    }

    private boolean oneApart(String a, String b) {
        int diff = 0;
        for (int i = 0; i < a.length() && diff <= 1; i++)
            if (a.charAt(i) != b.charAt(i)) diff++;
        return diff == 1;
    }
}
