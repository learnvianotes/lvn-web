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

    getNewsFeed(userId) {
        const users = new Set(this.following.get(userId) || []);
        users.add(userId);

        const allTweets = [];

        for (const user of users) {
            allTweets.push(...(this.tweets.get(user) || []));
        }

        allTweets.sort((a, b) => b[0] - a[0]);

        return allTweets.slice(0, 10).map(([, tweetId]) => tweetId);
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
}
