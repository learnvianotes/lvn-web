class Solution {
public:
    int reverse(int x) {
        int sign = x < 0 ? -1 : 1;
        long long value = llabs((long long)x);  // abs(INT_MIN) overflows int

        string digits = to_string(value);
        std::reverse(digits.begin(), digits.end());
        long long reversedNum = stoll(digits);
        reversedNum *= sign;

        if (reversedNum < INT_MIN || reversedNum > INT_MAX) {
            return 0;
        }

        return (int)reversedNum;
    }
};
