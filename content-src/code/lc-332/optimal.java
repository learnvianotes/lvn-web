class Solution {
    private Map<String, List<String>> graph = new HashMap<>();
    private List<String> itinerary = new ArrayList<>();

    public List<String> findItinerary(List<List<String>> tickets) {
        List<List<String>> sorted = new ArrayList<>(tickets);
        sorted.sort((a, b) -> a.get(0).equals(b.get(0))
                ? b.get(1).compareTo(a.get(1))
                : b.get(0).compareTo(a.get(0)));

        for (List<String> t : sorted)
            graph.computeIfAbsent(t.get(0), k -> new ArrayList<>()).add(t.get(1));

        dfs("JFK");
        Collections.reverse(itinerary);
        return itinerary;
    }

    private void dfs(String airport) {
        List<String> destinations = graph.getOrDefault(airport, new ArrayList<>());

        while (!destinations.isEmpty()) {
            String next = destinations.remove(destinations.size() - 1);
            dfs(next);
        }

        itinerary.add(airport);
    }
}
