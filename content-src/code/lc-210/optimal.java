class Solution {
    public int[] findOrder(int numCourses, int[][] prerequisites) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < numCourses; i++) graph.add(new ArrayList<>());
        int[] indegree = new int[numCourses];

        for (int[] p : prerequisites) {
            graph.get(p[1]).add(p[0]);
            indegree[p[0]]++;
        }

        Deque<Integer> queue = new ArrayDeque<>();
        for (int i = 0; i < numCourses; i++)
            if (indegree[i] == 0) queue.offer(i);

        int[] result = new int[numCourses];
        int size = 0;

        while (!queue.isEmpty()) {
            int course = queue.poll();
            result[size++] = course;

            for (int next : graph.get(course))
                if (--indegree[next] == 0) queue.offer(next);
        }

        return size == numCourses ? result : new int[0];
    }
}
