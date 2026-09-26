class Solution {
public:
    string multiply(string num1, string num2) {
        if (num1 == "0" || num2 == "0") {
            return "0";
        }

        int n = num1.size();
        int m = num2.size();
        vector<int> result(n + m, 0);

        for (int i = n - 1; i >= 0; i--) {
            for (int j = m - 1; j >= 0; j--) {
                int product = (num1[i] - '0') * (num2[j] - '0');
                int pos = i + j + 1;

                result[pos] += product;
                result[pos - 1] += result[pos] / 10;
                result[pos] %= 10;
            }
        }

        // Strip leading zeros
        int start = 0;
        while (start < (int)result.size() - 1 && result[start] == 0) {
            start++;
        }

        string answer;
        for (int k = start; k < (int)result.size(); k++) {
            answer += to_string(result[k]);
        }
        return answer;
    }
};
