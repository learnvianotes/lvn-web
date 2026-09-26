class KthLargest {
    private int k;
    private List<Integer> nums = new ArrayList<>();

    public KthLargest(int k, int[] nums) {
        this.k = k;
        for (int num : nums) this.nums.add(num);
    }

    public int add(int val) {
        nums.add(val);
        nums.sort(Collections.reverseOrder());

        return nums.get(k - 1);
    }
}
