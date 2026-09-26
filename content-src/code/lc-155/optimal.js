class MinStack {
    constructor() {
        this.stack = [];
        this.minimum = [];
    }

    push(val) {
        this.stack.push(val);
        if (!this.minimum.length) this.minimum.push(val);
        else this.minimum.push(Math.min(val, this.minimum[this.minimum.length - 1]));
    }

    pop() {
        this.minimum.pop();
        this.stack.pop();
    }

    top() { return this.stack[this.stack.length - 1]; }

    getMin() { return this.minimum[this.minimum.length - 1]; }
}
