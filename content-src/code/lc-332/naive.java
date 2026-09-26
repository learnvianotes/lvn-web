class Solution {
    private List<List<String>> tickets;
    private Map<String, List<Integer>> graph = new HashMap<>();
    private boolean[] used;
    private List<String> path = new ArrayList<>();

    public List<String> findItinerary(List<List<String>> tickets) {
        this.tickets = new ArrayList<>(tickets);
        this.tickets.sort((a, b) -> a.get(0).equals(b.get(0))
                ? a.get(1).compareTo(b.get(1))
                : a.get(0).compareTo(b.get(0)));

        // airport -> indices of its tickets, in lexical order of destination
        for (int i = 0; i < this.tickets.size(); i++)
            graph.computeIfAbsent(this.tickets.get(i).get(0), k -> new ArrayList<>()).add(i);

        used = new boolean[this.tickets.size()];
        path.add("JFK");
        dfs("JFK");

        return path;
    }

    private boolean dfs(String airport) {
        if (path.size() == tickets.size() + 1) return true;

        for (int i : graph.getOrDefault(airport, Collections.emptyList())) {
            if (used[i]) continue;

            String next = tickets.get(i).get(1);
            used[i] = true;
            path.add(next);

            if (dfs(next)) return true;

            used[i] = false;  // backtrack
            path.remove(path.size() - 1);
        }

        return false;
    }
}
