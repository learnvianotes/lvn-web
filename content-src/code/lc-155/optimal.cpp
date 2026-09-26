class MinStack {
    vector<int> stack, minimum;
public:
    MinStack() {}

    void push(int val) {
        stack.push_back(val);
        if (minimum.empty()) minimum.push_back(val);
        else minimum.push_back(min(val, minimum.back()));
    }

    void pop() {
        minimum.pop_back();
        stack.pop_back();
    }

    int top() { return stack.back(); }

    int getMin() { return minimum.back(); }
};
