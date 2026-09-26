class Solution {
    private List<List<Integer>> graph = new ArrayList<>();
    private boolean[] visiting, visited;

    public boolean canFinish(int numCourses, int[][] prerequisites) {
        for (int i = 0; i < numCourses; i++) graph.add(new ArrayList<>());

        for (int[] p : prerequisites)
            graph.get(p[0]).add(p[1]);

        visiting = new boolean[numCourses];
        visited = new boolean[numCourses];

        for (int course = 0; course < numCourses; course++)
            if (!dfs(course)) return false;

        return true;
    }

    private boolean dfs(int course) {
        if (visiting[course]) return false;
        if (visited[course]) return true;

        visiting[course] = true;

        for (int prerequisite : graph.get(course))
            if (!dfs(prerequisite)) return false;

        visiting[course] = false;
        visited[course] = true;

        return true;
    }
}
