class MinStack {
    private Deque<Integer> stack = new ArrayDeque<>();
    private Deque<Integer> minimum = new ArrayDeque<>();

    public MinStack() {}

    public void push(int val) {
        stack.push(val);
        if (minimum.isEmpty()) minimum.push(val);
        else minimum.push(Math.min(val, minimum.peek()));
    }

    public void pop() {
        minimum.pop();
        stack.pop();
    }

    public int top() { return stack.peek(); }

    public int getMin() { return minimum.peek(); }
}
