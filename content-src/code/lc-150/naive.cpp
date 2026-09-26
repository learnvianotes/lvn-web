class Solution {
public:
    int evalRPN(vector<string>& tokens) {
        vector<string> t = tokens;
        while (t.size() > 1) {
            for (int i = 0; i < t.size(); i++) {
                const string& token = t[i];
                if (token != "+" && token != "-" && token != "*" && token != "/") continue;
                int a = stoi(t[i - 2]), b = stoi(t[i - 1]);
                int result;
                if (token == "+") result = a + b;
                else if (token == "-") result = a - b;
                else if (token == "*") result = a * b;
                else result = a / b;
                t.erase(t.begin() + i - 2, t.begin() + i + 1);
                t.insert(t.begin() + i - 2, to_string(result));
                break;
            }
        }
        return stoi(t[0]);
    }
};
