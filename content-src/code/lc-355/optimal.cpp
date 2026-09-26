class Twitter {
    int time = 0;
    unordered_map<int, vector<pair<int, int>>> tweets;  // user -> {time, tweetId}
    unordered_map<int, unordered_set<int>> following;

public:
    Twitter() {}

    void postTweet(int userId, int tweetId) {
        time++;

        tweets[userId].push_back({time, tweetId});
    }

    void follow(int followerId, int followeeId) {
        if (followerId != followeeId) following[followerId].insert(followeeId);
    }

    void unfollow(int followerId, int followeeId) {
        following[followerId].erase(followeeId);
    }

    vector<int> getNewsFeed(int userId) {
        unordered_set<int> users = following[userId];
        users.insert(userId);

        priority_queue<array<int, 4>> heap;  // max-heap of {time, tweetId, user, index}

        for (int user : users) {
            auto& userTweets = tweets[user];

            if (!userTweets.empty()) {
                int index = userTweets.size() - 1;
                auto [time, tweetId] = userTweets[index];

                heap.push({time, tweetId, user, index});
            }
        }

        vector<int> result;

        while (!heap.empty() && result.size() < 10) {
            auto [_, tweetId, user, index] = heap.top();
            heap.pop();

            result.push_back(tweetId);

            index--;

            if (index >= 0) {
                auto [time, nextTweetId] = tweets[user][index];

                heap.push({time, nextTweetId, user, index});
            }
        }

        return result;
    }
};
