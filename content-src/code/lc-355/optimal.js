class MinHeap {
    constructor(compare = (a, b) => a - b, items = []) {
        this.compare = compare;
        this.data = items;
        for (let i = (items.length >> 1) - 1; i >= 0; i--) this.siftDown(i);
    }

    size() { return this.data.length; }

    peek() { return this.data[0]; }

    push(value) {
        const data = this.data;
        data.push(value);
        let i = data.length - 1;
        while (i > 0) {
            const parent = (i - 1) >> 1;
            if (this.compare(data[i], data[parent]) >= 0) break;
            [data[i], data[parent]] = [data[parent], data[i]];
            i = parent;
        }
    }

    pop() {
        const data = this.data;
        const top = data[0];
        const last = data.pop();
        if (data.length > 0) {
            data[0] = last;
            this.siftDown(0);
        }
        return top;
    }

    siftDown(i) {
        const data = this.data;
        while (true) {
            const left = 2 * i + 1, right = left + 1;
            let smallest = i;
            if (left < data.length && this.compare(data[left], data[smallest]) < 0) smallest = left;
            if (right < data.length && this.compare(data[right], data[smallest]) < 0) smallest = right;
            if (smallest === i) return;
            [data[i], data[smallest]] = [data[smallest], data[i]];
            i = smallest;
        }
    }
}

class Twitter {
    constructor() {
        this.time = 0;
        this.tweets = new Map();     // user -> [[time, tweetId], ...]
        this.following = new Map();  // user -> Set of followees
    }

    postTweet(userId, tweetId) {
        this.time++;

        if (!this.tweets.has(userId)) this.tweets.set(userId, []);
        this.tweets.get(userId).push([this.time, tweetId]);
    }

    follow(followerId, followeeId) {
        if (followerId !== followeeId) {
            if (!this.following.has(followerId)) this.following.set(followerId, new Set());
            this.following.get(followerId).add(followeeId);
        }
    }

    unfollow(followerId, followeeId) {
        this.following.get(followerId)?.delete(followeeId);
    }

    getNewsFeed(userId) {
        const users = new Set(this.following.get(userId) || []);
        users.add(userId);

        const heap = new MinHeap((a, b) => b[0] - a[0]);  // max-heap by time

        for (const user of users) {
            const tweets = this.tweets.get(user) || [];

            if (tweets.length) {
                const index = tweets.length - 1;
                const [time, tweetId] = tweets[index];

                heap.push([time, tweetId, user, index]);
            }
        }

        const result = [];

        while (heap.size() > 0 && result.length < 10) {
            let [, tweetId, user, index] = heap.pop();

            result.push(tweetId);

            index--;

            if (index >= 0) {
                const [time, nextTweetId] = this.tweets.get(user)[index];

                heap.push([time, nextTweetId, user, index]);
            }
        }

        return result;
    }
}
