class Solution {
    public List<String> letterCombinations(String digits) {
        List<String> result = new ArrayList<>();
        if (digits.isEmpty()) return result;

        Map<Character, String> phone = Map.of(
            '2', "abc", '3', "def", '4', "ghi", '5', "jkl",
            '6', "mno", '7', "pqrs", '8', "tuv", '9', "wxyz"
        );

        backtrack(digits, 0, phone, new StringBuilder(), result);
        return result;
    }

    private void backtrack(String digits, int index, Map<Character, String> phone,
                           StringBuilder current, List<String> result) {
        if (index == digits.length()) {
            result.add(current.toString());
            return;
        }

        for (char ch : phone.get(digits.charAt(index)).toCharArray()) {
            current.append(ch);
            backtrack(digits, index + 1, phone, current, result);
            current.deleteCharAt(current.length() - 1);
        }
    }
}
