class Solution {
    public List<List<Integer>> subsetsWithDup(int[] nums) {
        Arrays.sort(nums);
        Set<List<Integer>> result = new HashSet<>();
        backtrack(nums, 0, new ArrayList<>(), result);
        return new ArrayList<>(result);
    }

    private void backtrack(int[] nums, int index, List<Integer> current, Set<List<Integer>> result) {
        if (index == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }

        // Don't take
        backtrack(nums, index + 1, current, result);

        // Take
        current.add(nums[index]);
        backtrack(nums, index + 1, current, result);
        current.remove(current.size() - 1);
    }
}
