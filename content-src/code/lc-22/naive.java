class Solution {
    public List<String> generateParenthesis(int n) {
        List<String> result = new ArrayList<>();
        generate("", n, result);
        return result;
    }

    private boolean valid(String s) {
        int balance = 0;
        for (char c : s.toCharArray()) {
            if (c == '(') balance++;
            else balance--;
            if (balance < 0) return false;
        }
        return balance == 0;
    }

    private void generate(String s, int n, List<String> result) {
        if (s.length() == 2 * n) {
            if (valid(s)) result.add(s);
            return;
        }
        generate(s + "(", n, result);
        generate(s + ")", n, result);
    }
}
