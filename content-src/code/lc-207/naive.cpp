class Solution {
public:
    bool canFinish(int numCourses, vector<vector<int>>& prerequisites) {
        vector<vector<int>> graph(numCourses);

        for (auto& p : prerequisites)
            graph[p[0]].push_back(p[1]);

        vector<bool> visiting(numCourses, false), visited(numCourses, false);

        function<bool(int)> dfs = [&](int course) -> bool {
            if (visiting[course]) return false;
            if (visited[course]) return true;

            visiting[course] = true;

            for (int prerequisite : graph[course])
                if (!dfs(prerequisite)) return false;

            visiting[course] = false;
            visited[course] = true;

            return true;
        };

        for (int course = 0; course < numCourses; course++)
            if (!dfs(course)) return false;

        return true;
    }
};
