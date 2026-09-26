class Solution {
    private List<List<Integer>> graph = new ArrayList<>();
    private int[] state;  // 0 = unvisited, 1 = visiting, 2 = done
    private int[] result;
    private int size = 0;

    public int[] findOrder(int numCourses, int[][] prerequisites) {
        for (int i = 0; i < numCourses; i++) graph.add(new ArrayList<>());

        for (int[] p : prerequisites)
            graph.get(p[0]).add(p[1]);

        state = new int[numCourses];
        result = new int[numCourses];

        for (int course = 0; course < numCourses; course++)
            if (!dfs(course)) return new int[0];

        return result;
    }

    private boolean dfs(int course) {
        if (state[course] == 1) return false;  // cycle
        if (state[course] == 2) return true;

        state[course] = 1;

        for (int prerequisite : graph.get(course))
            if (!dfs(prerequisite)) return false;

        state[course] = 2;
        result[size++] = course;  // after all its prerequisites

        return true;
    }
}
