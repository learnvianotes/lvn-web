class Solution {
public:
    vector<int> plusOne(vector<int>& digits) {
        // C++ has no built-in big integer (digits can be 100 long),
        // so the "number" is kept as a decimal string
        string number;

        for (int digit : digits) {
            number += char('0' + digit);
        }

        // number += 1
        int i = number.size() - 1;
        while (i >= 0 && number[i] == '9') {
            number[i--] = '0';
        }
        if (i < 0) {
            number.insert(number.begin(), '1');
        } else {
            number[i]++;
        }

        vector<int> result;
        for (char d : number) {
            result.push_back(d - '0');
        }
        return result;
    }
};
