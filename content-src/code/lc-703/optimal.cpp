class KthLargest {
    int k;
    priority_queue<int, vector<int>, greater<int>> heap;  // min-heap

public:
    KthLargest(int k, vector<int>& nums) : k(k), heap(nums.begin(), nums.end()) {
        while ((int)heap.size() > k) heap.pop();
    }

    int add(int val) {
        heap.push(val);

        if ((int)heap.size() > k) heap.pop();

        return heap.top();
    }
};
