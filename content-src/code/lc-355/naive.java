class Twitter {
    private int time = 0;
    private Map<Integer, List<int[]>> tweets = new HashMap<>();  // user -> {time, tweetId}
    private Map<Integer, Set<Integer>> following = new HashMap<>();

    public Twitter() {}

    public void postTweet(int userId, int tweetId) {
        time++;

        tweets.computeIfAbsent(userId, key -> new ArrayList<>()).add(new int[]{time, tweetId});
    }

    public List<Integer> getNewsFeed(int userId) {
        Set<Integer> users = new HashSet<>(following.getOrDefault(userId, new HashSet<>()));
        users.add(userId);

        List<int[]> allTweets = new ArrayList<>();

        for (int user : users) {
            allTweets.addAll(tweets.getOrDefault(user, new ArrayList<>()));
        }

        allTweets.sort((a, b) -> Integer.compare(b[0], a[0]));

        List<Integer> result = new ArrayList<>();
        for (int i = 0; i < allTweets.size() && i < 10; i++) {
            result.add(allTweets.get(i)[1]);
        }

        return result;
    }

    public void follow(int followerId, int followeeId) {
        if (followerId != followeeId) {
            following.computeIfAbsent(followerId, key -> new HashSet<>()).add(followeeId);
        }
    }

    public void unfollow(int followerId, int followeeId) {
        Set<Integer> followees = following.get(followerId);
        if (followees != null) followees.remove(followeeId);
    }
}
