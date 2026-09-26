class Solution {
public:
    bool checkInclusion(string s1, string s2) {
        unordered_set<string> target;
        sort(s1.begin(), s1.end());
        do target.insert(s1); while (next_permutation(s1.begin(), s1.end()));
        int length = s1.size();
        for (int i = 0; i + length <= (int)s2.size(); i++)
            if (target.count(s2.substr(i, length))) return true;
        return false;
    }
};
