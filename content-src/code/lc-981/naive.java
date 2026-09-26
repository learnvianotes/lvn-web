class TimeMap {
    private Map<String, List<Pair>> store;

    private static class Pair {
        int time;
        String value;

        Pair(int time, String value) {
            this.time = time;
            this.value = value;
        }
    }

    public TimeMap() {
        store = new HashMap<>();
    }

    public void set(String key, String value, int timestamp) {
        store.computeIfAbsent(key, k -> new ArrayList<>()).add(new Pair(timestamp, value));
    }

    public String get(String key, int timestamp) {
        if (!store.containsKey(key)) {
            return "";
        }

        List<Pair> values = store.get(key);

        for (int i = values.size() - 1; i >= 0; i--) {
            if (values.get(i).time <= timestamp) {
                return values.get(i).value;
            }
        }

        return "";
    }
}
