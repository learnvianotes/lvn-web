class Solution {
public:
    vector<int> partitionLabels(string s) {
        vector<int> result;
        int n = s.size();
        int start = 0;

        while (start < n) {
            unordered_set<char> chars;
            int end = start;

            while (end < n) {
                chars.insert(s[end]);

                int last = 0;
                for (int i = 0; i < n; i++) {
                    if (chars.count(s[i])) {
                        last = i;
                    }
                }

                if (last == end) {
                    break;
                }

                end++;
            }

            result.push_back(end - start + 1);
            start = end + 1;
        }

        return result;
    }
};
