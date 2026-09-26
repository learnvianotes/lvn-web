class Solution {
    public int leastInterval(char[] tasks, int n) {
        Map<Character, Integer> count = new HashMap<>();
        for (char task : tasks) count.merge(task, 1, Integer::sum);

        int time = 0;

        while (!count.isEmpty()) {
            int executed = 0;

            // Sort by frequency each round
            List<Character> available = new ArrayList<>(count.keySet());
            available.sort((a, b) -> Integer.compare(count.get(b), count.get(a)));

            for (int i = 0; i < available.size() && i < n + 1; i++) {
                char task = available.get(i);
                int freq = count.get(task) - 1;
                executed++;

                if (freq == 0) count.remove(task);
                else count.put(task, freq);
            }

            if (!count.isEmpty()) time += n + 1;
            else time += executed;
        }

        return time;
    }
}
