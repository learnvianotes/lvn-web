class MedianFinder {
    private PriorityQueue<Integer> small = new PriorityQueue<>(Collections.reverseOrder());  // max-heap
    private PriorityQueue<Integer> large = new PriorityQueue<>();                            // min-heap

    public MedianFinder() {}

    public void addNum(int num) {
        small.offer(num);

        // Ensure every small <= every large
        if (!small.isEmpty() && !large.isEmpty() && small.peek() > large.peek()) {
            large.offer(small.poll());
        }

        // Balance sizes
        if (small.size() > large.size() + 1) {
            large.offer(small.poll());
        } else if (large.size() > small.size()) {
            small.offer(large.poll());
        }
    }

    public double findMedian() {
        if (small.size() > large.size()) return small.peek();

        return (small.peek() + large.peek()) / 2.0;
    }
}
