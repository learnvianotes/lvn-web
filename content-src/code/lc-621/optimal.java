class Solution {
    public int leastInterval(char[] tasks, int n) {
        Map<Character, Integer> count = new HashMap<>();
        for (char task : tasks) count.merge(task, 1, Integer::sum);

        // max-heap of remaining counts
        PriorityQueue<Integer> heap = new PriorityQueue<>(Collections.reverseOrder());
        heap.addAll(count.values());

        Deque<int[]> cooldown = new ArrayDeque<>();  // {remaining, time it becomes available}

        int time = 0;

        while (!heap.isEmpty() || !cooldown.isEmpty()) {
            time++;

            // Add tasks whose cooldown is over
            while (!cooldown.isEmpty() && cooldown.peekFirst()[1] == time) {
                heap.offer(cooldown.pollFirst()[0]);
            }

            if (!heap.isEmpty()) {
                int freq = heap.poll() - 1;

                if (freq != 0) cooldown.offerLast(new int[]{freq, time + n + 1});
            }
        }

        return time;
    }
}
