class MedianFinder {
    constructor() {
        this.nums = [];
    }

    addNum(num) {
        this.nums.push(num);
    }

    findMedian() {
        this.nums.sort((a, b) => a - b);

        const n = this.nums.length;

        if (n % 2) return this.nums[n >> 1];

        return (this.nums[n / 2 - 1] + this.nums[n / 2]) / 2;
    }
}
