class Solution {
    public int[] topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> count = new HashMap<>();
        for (int n : nums) count.put(n, count.getOrDefault(n, 0) + 1);
        List<List<Integer>> buckets = new ArrayList<>();
        for (int i = 0; i <= nums.length; i++) buckets.add(new ArrayList<>());
        for (Map.Entry<Integer, Integer> e : count.entrySet())
            buckets.get(e.getValue()).add(e.getKey());
        int[] res = new int[k];
        int idx = 0;
        for (int i = buckets.size() - 1; i > 0; i--)
            for (int num : buckets.get(i)) {
                res[idx++] = num;
                if (idx == k) return res;
            }
        return res;
    }
}
