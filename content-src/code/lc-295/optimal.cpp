class MedianFinder {
    priority_queue<int> small;                             // max-heap
    priority_queue<int, vector<int>, greater<int>> large;  // min-heap

public:
    MedianFinder() {}

    void addNum(int num) {
        small.push(num);

        // Ensure every small <= every large
        if (!small.empty() && !large.empty() && small.top() > large.top()) {
            large.push(small.top());
            small.pop();
        }

        // Balance sizes
        if (small.size() > large.size() + 1) {
            large.push(small.top());
            small.pop();
        } else if (large.size() > small.size()) {
            small.push(large.top());
            large.pop();
        }
    }

    double findMedian() {
        if (small.size() > large.size()) return small.top();

        return (small.top() + large.top()) / 2.0;
    }
};
