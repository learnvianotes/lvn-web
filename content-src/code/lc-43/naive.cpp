class Solution {
public:
    string multiply(string num1, string num2) {
        // C++ has no built-in big integer, so the closest shortcut is
        // "num1 * digit, shifted" for each digit of num2, summed up
        string total = "0";

        for (int j = 0; j < (int)num2.size(); j++) {
            total = add(total + "0", times(num1, num2[j] - '0'));
        }

        int start = 0;
        while (start < (int)total.size() - 1 && total[start] == '0') {
            start++;
        }
        return total.substr(start);
    }

private:
    string times(const string& num, int digit) {
        string result;
        int carry = 0;
        for (int i = num.size() - 1; i >= 0; i--) {
            int value = (num[i] - '0') * digit + carry;
            result += char('0' + value % 10);
            carry = value / 10;
        }
        if (carry) result += char('0' + carry);
        reverse(result.begin(), result.end());
        return result;
    }

    string add(const string& a, const string& b) {
        string result;
        int i = a.size() - 1, j = b.size() - 1, carry = 0;
        while (i >= 0 || j >= 0 || carry) {
            int value = carry;
            if (i >= 0) value += a[i--] - '0';
            if (j >= 0) value += b[j--] - '0';
            result += char('0' + value % 10);
            carry = value / 10;
        }
        reverse(result.begin(), result.end());
        return result;
    }
};
