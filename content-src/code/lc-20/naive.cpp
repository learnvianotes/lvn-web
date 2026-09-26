class Solution {
public:
    bool isValid(string s) {
        bool changed = true;
        while (changed) {
            changed = false;
            for (string pair : {"()", "[]", "{}"}) {
                if (s.find(pair) != string::npos) {
                    s = replaceAll(s, pair);
                    changed = true;
                }
            }
        }
        return s.empty();
    }

private:
    string replaceAll(const string& s, const string& pair) {
        string out;
        for (size_t i = 0; i < s.size(); ) {
            if (s.compare(i, 2, pair) == 0) i += 2;
            else out += s[i++];
        }
        return out;
    }
};
