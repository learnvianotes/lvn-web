class Solution {
public:
    string minWindow(string s, string t) {
        if (t.empty()) return "";
        string answer = "";
        for (int left = 0; left < s.size(); left++) {
            unordered_map<char, int> count;
            for (int right = left; right < s.size(); right++) {
                count[s[right]]++;
                bool valid = true;
                for (char c : t)
                    if (count[c] < std::count(t.begin(), t.end(), c)) {
                        valid = false;
                        break;
                    }
                if (valid) {
                    string current = s.substr(left, right - left + 1);
                    if (answer.empty() || current.size() < answer.size()) answer = current;
                    break;
                }
            }
        }
        return answer;
    }
};
