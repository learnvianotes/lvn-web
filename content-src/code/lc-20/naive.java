class Solution {
    public boolean isValid(String s) {
        boolean changed = true;
        while (changed) {
            changed = false;
            for (String pair : new String[]{"()", "[]", "{}"}) {
                if (s.contains(pair)) {
                    s = s.replace(pair, "");
                    changed = true;
                }
            }
        }
        return s.isEmpty();
    }
}
