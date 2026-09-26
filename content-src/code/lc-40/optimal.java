class Solution {
    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        Arrays.sort(candidates);
        List<List<Integer>> result = new ArrayList<>();
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
            // Skip duplicate choices at the same level
            if (i > start && candidates[i] == candidates[i - 1]) continue;

            // Since sorted, no later value can work
            if (candidates[i] > remaining) break;

            current.add(candidates[i]);

            // i + 1 because each element can be used once
            backtrack(candidates, i + 1, remaining - candidates[i], current, result);

            current.remove(current.size() - 1);
        }
    }
}
