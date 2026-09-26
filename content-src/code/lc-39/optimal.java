class Solution {
    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        List<List<Integer>> result = new ArrayList<>();
        Arrays.sort(candidates);
        backtrack(candidates, 0, target, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] candidates, int start, int remaining, List<Integer> current,
                           List<List<Integer>> result) {
        if (remaining == 0) {
            result.add(new ArrayList<>(current));
            return;
        }

        for (int i = start; i < candidates.length; i++) {
            int num = candidates[i];

            if (num > remaining) break;

            current.add(num);

            // i, not i + 1, because we can reuse the same number
            backtrack(candidates, i, remaining - num, current, result);

            current.remove(current.size() - 1);
        }
    }
}
