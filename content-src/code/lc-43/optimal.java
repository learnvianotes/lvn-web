class Solution {
    public String multiply(String num1, String num2) {
        if (num1.equals("0") || num2.equals("0")) {
            return "0";
        }

        int n = num1.length();
        int m = num2.length();
        int[] result = new int[n + m];

        for (int i = n - 1; i >= 0; i--) {
            for (int j = m - 1; j >= 0; j--) {
                int product = (num1.charAt(i) - '0') * (num2.charAt(j) - '0');
                int pos = i + j + 1;

                result[pos] += product;
                result[pos - 1] += result[pos] / 10;
                result[pos] %= 10;
            }
        }

        // Strip leading zeros
        int start = 0;
        while (start < result.length - 1 && result[start] == 0) {
            start++;
        }

        StringBuilder answer = new StringBuilder();
        for (int k = start; k < result.length; k++) {
            answer.append(result[k]);
        }
        return answer.toString();
    }
}
