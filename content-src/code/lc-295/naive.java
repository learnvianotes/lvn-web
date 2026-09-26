class MedianFinder {
    private List<Integer> nums = new ArrayList<>();

    public MedianFinder() {}

    public void addNum(int num) {
        nums.add(num);
    }

    public double findMedian() {
        Collections.sort(nums);

        int n = nums.size();

        if (n % 2 == 1) return nums.get(n / 2);

        return (nums.get(n / 2 - 1) + nums.get(n / 2)) / 2.0;
    }
}
