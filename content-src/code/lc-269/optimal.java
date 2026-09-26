class Solution {
    private Map<Character, Set<Character>> graph = new LinkedHashMap<>();
    // true = on the current path (cycle), false = finished
    private Map<Character, Boolean> visited = new HashMap<>();
    private StringBuilder result = new StringBuilder();

    public String alienOrder(String[] words) {
        for (String word : words)
            for (char c : word.toCharArray())
                graph.putIfAbsent(c, new HashSet<>());

        for (int i = 0; i + 1 < words.length; i++) {
            String w1 = words[i], w2 = words[i + 1];
            int minLength = Math.min(w1.length(), w2.length());

            if (w1.length() > w2.length() && w1.startsWith(w2))
                return "";

            for (int j = 0; j < minLength; j++) {
                if (w1.charAt(j) != w2.charAt(j)) {
                    graph.get(w1.charAt(j)).add(w2.charAt(j));
                    break;
                }
            }
        }

        for (char c : graph.keySet())
            if (dfs(c)) return "";

        return result.reverse().toString();
    }

    private boolean dfs(char c) {
        if (visited.containsKey(c)) return visited.get(c);

        visited.put(c, true);

        for (char neighbor : graph.get(c))
            if (dfs(neighbor)) return true;

        visited.put(c, false);
        result.append(c);

        return false;
    }
}
