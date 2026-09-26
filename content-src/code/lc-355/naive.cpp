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

    vector<int> getNewsFeed(int userId) {
        unordered_set<int> users = following[userId];
        users.insert(userId);

        vector<pair<int, int>> allTweets;

        for (int user : users) {
            allTweets.insert(allTweets.end(), tweets[user].begin(), tweets[user].end());
        }

        sort(allTweets.begin(), allTweets.end(), greater<pair<int, int>>());

        vector<int> result;
        for (int i = 0; i < (int)allTweets.size() && i < 10; i++) {
            result.push_back(allTweets[i].second);
        }

        return result;
    }

    void follow(int followerId, int followeeId) {
        if (followerId != followeeId) following[followerId].insert(followeeId);
    }

    void unfollow(int followerId, int followeeId) {
        following[followerId].erase(followeeId);
    }
};
