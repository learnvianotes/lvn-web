class Solution {
public:
    bool mergeTriplets(vector<vector<int>>& triplets, vector<int>& target) {
        return dfs(triplets, target, 0, {0, 0, 0});
    }

private:
    bool dfs(vector<vector<int>>& triplets, vector<int>& target, int index, vector<int> current) {
        if (current == target) {
            return true;
        }

        if (index == (int)triplets.size()) {
            return false;
        }

        if (dfs(triplets, target, index + 1, current)) {
            return true;
        }

        vector<int>& triplet = triplets[index];

        if (triplet[0] <= target[0] && triplet[1] <= target[1] && triplet[2] <= target[2]) {
            vector<int> merged(3);
            for (int i = 0; i < 3; i++) {
                merged[i] = max(current[i], triplet[i]);
            }

            if (dfs(triplets, target, index + 1, merged)) {
                return true;
            }
        }

        return false;
    }
};
