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

        int left = 0;
        int right = values.size() - 1;

        String answer = "";

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (values.get(mid).time <= timestamp) {
                answer = values.get(mid).value;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return answer;
    }
}
