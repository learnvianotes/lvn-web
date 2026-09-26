class Solution {
    public int evalRPN(String[] tokens) {
        Deque<Integer> stack = new ArrayDeque<>();
        Set<String> operators = Set.of("+", "-", "*", "/");
        for (String token : tokens) {
            if (!operators.contains(token)) {
                stack.push(Integer.parseInt(token));
                continue;
            }
            int b = stack.pop();
            int a = stack.pop();
            int result;
            if (token.equals("+")) result = a + b;
            else if (token.equals("-")) result = a - b;
            else if (token.equals("*")) result = a * b;
            else result = a / b;
            stack.push(result);
        }
        return stack.peek();
    }
}
