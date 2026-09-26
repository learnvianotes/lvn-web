class Solution {
    public int carFleet(int target, int[] position, int[] speed) {
        int n = position.length;
        int[][] cars = new int[n][];
        for (int i = 0; i < n; i++) cars[i] = new int[]{position[i], speed[i]};
        Arrays.sort(cars, (x, y) -> Integer.compare(x[0], y[0]));
        Deque<Double> fleets = new ArrayDeque<>();
        for (int[] car : cars) {
            double time = (double) (target - car[0]) / car[1];
            while (!fleets.isEmpty() && fleets.peek() <= time) fleets.pop();
            fleets.push(time);
        }
        return fleets.size();
    }
}
