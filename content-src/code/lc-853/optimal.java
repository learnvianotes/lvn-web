class Solution {
    public int carFleet(int target, int[] position, int[] speed) {
        int n = position.length;
        int[][] cars = new int[n][];
        for (int i = 0; i < n; i++) cars[i] = new int[]{position[i], speed[i]};
        Arrays.sort(cars, (x, y) -> Integer.compare(y[0], x[0]));
        Deque<Double> stack = new ArrayDeque<>();
        for (int[] car : cars) {
            double time = (double) (target - car[0]) / car[1];
            if (stack.isEmpty() || time > stack.peek()) stack.push(time);
        }
        return stack.size();
    }
}
