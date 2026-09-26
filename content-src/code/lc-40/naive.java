class Solution {
    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        Set<List<Integer>> result = new HashSet<>();
        Arrays.sort(candidates);
        backtrack(candidates, 0, target, new ArrayList<>(), result);
        return new ArrayList<>(result);
    }

    private void backtrack(int[] candidates, int index, int remaining, List<Integer> current,
                           Set<List<Integer>> result) {
        if (remaining == 0) {
            result.add(new ArrayList<>(current));
            return;
        }

        if (index == candidates.length || remaining < 0) return;

        // Don't choose
        backtrack(candidates, index + 1, remaining, current, result);

        // Choose
        current.add(candidates[index]);
        backtrack(candidates, index + 1, remaining - candidates[index], current, result);
        current.remove(current.size() - 1);
    }
}
