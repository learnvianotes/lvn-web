class Solution {
    public boolean mergeTriplets(int[][] triplets, int[] target) {
        return dfs(triplets, target, 0, new int[]{0, 0, 0});
    }

    private boolean dfs(int[][] triplets, int[] target, int index, int[] current) {
        if (Arrays.equals(current, target)) {
            return true;
        }

        if (index == triplets.length) {
            return false;
        }

        if (dfs(triplets, target, index + 1, current)) {
            return true;
        }

        int[] triplet = triplets[index];

        if (triplet[0] <= target[0] && triplet[1] <= target[1] && triplet[2] <= target[2]) {
            int[] merged = new int[3];
            for (int i = 0; i < 3; i++) {
                merged[i] = Math.max(current[i], triplet[i]);
            }

            if (dfs(triplets, target, index + 1, merged)) {
                return true;
            }
        }

        return false;
    }
}
