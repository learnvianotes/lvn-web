class Twitter {
    private int time = 0;
    private Map<Integer, List<int[]>> tweets = new HashMap<>();  // user -> {time, tweetId}
    private Map<Integer, Set<Integer>> following = new HashMap<>();

    public Twitter() {}

    public void postTweet(int userId, int tweetId) {
        time++;

        tweets.computeIfAbsent(userId, key -> new ArrayList<>()).add(new int[]{time, tweetId});
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

    public List<Integer> getNewsFeed(int userId) {
        Set<Integer> users = new HashSet<>(following.getOrDefault(userId, new HashSet<>()));
        users.add(userId);

        // max-heap of {time, tweetId, user, index}
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> Integer.compare(b[0], a[0]));

        for (int user : users) {
            List<int[]> userTweets = tweets.getOrDefault(user, new ArrayList<>());

            if (!userTweets.isEmpty()) {
                int index = userTweets.size() - 1;
                int[] tweet = userTweets.get(index);

                heap.offer(new int[]{tweet[0], tweet[1], user, index});
            }
        }

        List<Integer> result = new ArrayList<>();

        while (!heap.isEmpty() && result.size() < 10) {
            int[] top = heap.poll();
            int user = top[2], index = top[3];

            result.add(top[1]);

            index--;

            if (index >= 0) {
                int[] tweet = tweets.get(user).get(index);

                heap.offer(new int[]{tweet[0], tweet[1], user, index});
            }
        }

        return result;
    }
}
