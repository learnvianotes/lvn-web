class Solution {
    public int evalRPN(String[] tokens) {
        List<String> t = new ArrayList<>(Arrays.asList(tokens));
        Set<String> operators = Set.of("+", "-", "*", "/");
        while (t.size() > 1) {
            for (int i = 0; i < t.size(); i++) {
                String token = t.get(i);
                if (!operators.contains(token)) continue;
                int a = Integer.parseInt(t.get(i - 2));
                int b = Integer.parseInt(t.get(i - 1));
                int result;
                if (token.equals("+")) result = a + b;
                else if (token.equals("-")) result = a - b;
                else if (token.equals("*")) result = a * b;
                else result = a / b;
                t.subList(i - 2, i + 1).clear();
                t.add(i - 2, String.valueOf(result));
                break;
            }
        }
        return Integer.parseInt(t.get(0));
    }
}
